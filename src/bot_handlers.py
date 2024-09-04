import os
import psycopg2
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Dispatcher, Bot


class GameStates(StatesGroup):
    waiting_for_answer = State()


def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💡 Help")],
            [KeyboardButton(text="🦾 About this bot")],
        ],
        resize_keyboard=True,
        selective=True,
    )
    return keyboard


async def show_welcome(message: Message, state: FSMContext):
    welcome_text = "Welcome to Spanish verbs game!\nSend /play to start a new game."
    await message.answer(welcome_text) #, reply_markup=get_main_keyboard()


async def show_help(message: Message, state: FSMContext):
    help_text = (
        "Welcome to Spanish verbs game!\n\n"
        "Available commands:\n"
        "/start - Start this bot.\n"
        "/help - Show this help message.\n"
        "/play - Begin new game.\n"
        "/about - About this bot.\n\n"
        "The game will offer verb in Spanish, tense and subject. "
        "Your task is to write correct corresponding verb form.\n"
        "¡Buena suerte!"
    )
    await message.answer(help_text) #, reply_markup=get_main_keyboard()


async def show_about(message: Message, state: FSMContext):
    about_text = (
        f"This bot was created by Denis to help learn Spanish."
    )
    await message.answer(about_text) # , reply_markup=get_main_keyboard()


def get_random_verb_form(cursor):
    cursor.execute('''
    SELECT verb_form.id, verb.name, tense.name, subject.name, verb_form.form, verb_form.example
    FROM verb_form
    JOIN verb ON verb.id=verb_form.verb_id
    JOIN tense ON tense.id=verb_form.tense_id
    JOIN subject ON subject.id=verb_form.subject_id
    ORDER BY RANDOM() LIMIT 1;
    ''')
    return cursor.fetchone()


async def start_game(message: Message, state: FSMContext):
    try:
        conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_DATABASE'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
        )
        cursor = conn.cursor()

    except Exception as e:
        await message.answer(f"Error connecting to database: {e}")
        return

    verb_form = get_random_verb_form(cursor)
    if not verb_form:
        await message.answer("There is no data for the game.")
        conn.close()
        return

    verb_form_id, verb, tense, subject, form, example = verb_form
    game_text = f"Verb: {verb}\nTense: {tense}\nSubject: {subject}\nWrite corresponding form of this verb:"
    await message.answer(game_text) # , reply_markup=get_main_keyboard()

    await state.update_data(verb_form_id=verb_form_id, correct_form=form, example=example)
    await state.set_state(GameStates.waiting_for_answer)
    conn.close()


async def play_game(message: Message, state: FSMContext):
    await start_game(message, state)


async def check_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    correct_form = user_data.get("correct_form")
    example = user_data.get("example")
    
    user_input = message.text.strip()
    if user_input.lower() == correct_form.lower():
        await message.answer(f"You are right! \n\nExample: {example}\n\n_") # , reply_markup=get_main_keyboard()
    else:
        await message.answer(f"Almost. Correct from is: {correct_form} \n\nExample: {example}\n\n_") # , reply_markup=get_main_keyboard()

    # Запускаем новую игру
    await start_game(message, state)


async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="🚀 Start the bot."),
        types.BotCommand(command="/help", description="💡 How this bot works."),
        types.BotCommand(command="/play", description="🎯 Start the game."),
        types.BotCommand(command="/about", description="🦾 About this bot."),
    ]
    await bot.set_my_commands(commands)


def register_handlers(dp: Dispatcher):
    dp.message.register(show_welcome, Command('start'))
    dp.message.register(show_help, Command('help'))
    dp.message.register(play_game, Command('play'))
    dp.message.register(show_about, Command('about')) #, lambda message: message["text"] == "🦾 Sobre este bot")
    dp.message.register(check_answer, GameStates.waiting_for_answer)
    dp.message.register(show_help)