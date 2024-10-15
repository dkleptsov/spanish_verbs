""" Handles user interactions, game states, and communication with the database. """

import os
from typing import Optional, Any, Tuple
import psycopg2
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Dispatcher, Bot


class GameStates(StatesGroup):
    """Class to define the states for the game."""
    waiting_for_answer = State()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create the main keyboard for the bot."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💡 Help")],
            [KeyboardButton(text="🦾 About this bot")],
        ],
        resize_keyboard=True,
        selective=True,
    )
    return keyboard


async def show_welcome(message: Message, state: FSMContext) -> None:
    """Send a welcome message to the user."""
    welcome_text = "Welcome to the Spanish verbs game!\nSend /play to start a new game."
    await message.answer(welcome_text)  # , reply_markup=get_main_keyboard()


async def show_help(message: Message, state: FSMContext) -> None:
    """Display help information to the user."""
    help_text = (
        "Welcome to the Spanish verbs game!\n\n"
        "Available commands:\n"
        "/start - Start this bot.\n"
        "/help - Show this help message.\n"
        "/play - Begin a new game.\n"
        "/about - About this bot.\n\n"
        "The game will offer a verb in Spanish, tense, and subject. "
        "Your task is to write the correct corresponding verb form.\n"
        "¡Buena suerte!"
    )
    await message.answer(help_text)  # , reply_markup=get_main_keyboard()


async def show_about(message: Message, state: FSMContext) -> None:
    """Provide information about the bot to the user."""
    about_text = (
        "This bot was created by Denis to help learn Spanish."
    )
    await message.answer(about_text)  # , reply_markup=get_main_keyboard()


def get_random_verb_form(cursor: Any) -> Optional[Tuple]:
    """Fetch a random verb form from the database."""
    cursor.execute('''
    SELECT verb_form.id, verb.name, tense.name, subject.name, verb_form.form, verb_form.example
    FROM verb_form
    JOIN verb ON verb.id=verb_form.verb_id
    JOIN tense ON tense.id=verb_form.tense_id
    JOIN subject ON subject.id=verb_form.subject_id
    ORDER BY RANDOM() LIMIT 1;
    ''')
    return cursor.fetchone()


async def start_game(message: Message, state: FSMContext) -> None:
    """Start a new game by fetching a random verb form."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_USER_PASSWORD')
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
    game_text = (
        f"Verb: {verb}\n"
        f"Tense: {tense}\n"
        f"Subject: {subject}\n"
        "Write the corresponding form of this verb:"
    )
    await message.answer(game_text)  # , reply_markup=get_main_keyboard()

    await state.update_data(verb_form_id=verb_form_id, correct_form=form, example=example)
    await state.set_state(GameStates.waiting_for_answer)
    conn.close()


async def play_game(message: Message, state: FSMContext) -> None:
    """Trigger the game to start."""
    await start_game(message, state)


async def check_answer(message: Message, state: FSMContext) -> None:
    """Check the user's answer against the correct verb form."""
    user_data = await state.get_data()
    correct_form = user_data.get("correct_form")
    example = user_data.get("example")

    user_input = message.text.strip()
    if user_input.lower() == correct_form.lower():
        await message.answer(f"You are right! \n\nExample: {example}\n\n_")  # , reply_markup=get_main_keyboard()
    else:
        await message.answer(f"Almost. The correct form is: {correct_form} \n\nExample: {example}\n\n_")  # , reply_markup=get_main_keyboard()

    # Start a new game
    await start_game(message, state)


async def set_bot_commands(bot: Bot) -> None:
    """Set the bot commands for the Telegram interface."""
    commands = [
        types.BotCommand(command="/start", description="🚀 Start the bot."),
        types.BotCommand(command="/help", description="💡 How this bot works."),
        types.BotCommand(command="/play", description="🎯 Start the game."),
        types.BotCommand(command="/about", description="🦾 About this bot."),
    ]
    await bot.set_my_commands(commands)


def register_handlers(dp: Dispatcher) -> None:
    """Register all command handlers for the bot."""
    dp.message.register(show_welcome, Command('start'))
    dp.message.register(show_help, Command('help'))
    dp.message.register(play_game, Command('play'))
    dp.message.register(show_about, Command('about'))  # , lambda message: message["text"] == "🦾 About this bot")
    dp.message.register(check_answer, GameStates.waiting_for_answer)
    dp.message.register(show_help)
