# handlers.py
import os
import sqlite3
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
            [KeyboardButton(text="💡 Ayuda")],
            [KeyboardButton(text="🦾 Sobre este bot")],
        ],
        resize_keyboard=True,
        selective=True,
    )
    return keyboard


async def show_welcome(message: Message, state: FSMContext):
    welcome_text = "¡Bienvenido al juego de los verbos en español!\nEscribe /play para empezar a jugar."
    await message.answer(welcome_text) #, reply_markup=get_main_keyboard()
    # await start_game(message, state)


async def show_help(message: Message, state: FSMContext):
    help_text = (
        "¡Bienvenido al juego de los verbos en español!\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar bot\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/play - Iniciar el juego\n"
        "/about - Sobre este bot\n\n"
        "En el juego se le ofrecerá verbos en español con el tiempo y el sujeto. "
        "Su tarea es escribir la forma correcta del verbo.\n"
        "¡Buena suerte!"
    )
    await message.answer(help_text) #, reply_markup=get_main_keyboard()


async def show_about(message: Message, state: FSMContext):
    about_text = (
        "Este bot fue creado por Denis para ayudar a aprender español."
    )
    await message.answer(about_text) # , reply_markup=get_main_keyboard()


def get_random_verb_form(cursor):
    cursor.execute('''
        SELECT verb_forms.id, verbs.verb, tenses.tense, subjects.subject, verb_forms.form
        FROM verb_forms
        JOIN verbs ON verb_forms.verb_id = verbs.id
        JOIN tenses ON verb_forms.tense_id = tenses.id
        JOIN subjects ON verb_forms.subject_id = subjects.id
        ORDER BY RANDOM() LIMIT 1
    ''')
    return cursor.fetchone()


async def start_game(message: Message, state: FSMContext):
    db_name = "data/verbs.db"
    if not os.path.exists(db_name):
        await message.answer(f"Base de datos no encontrada en: {db_name}")
        return
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        await message.answer(f"Error al conectarse a la base de datos: {e}")
        return

    verb_form = get_random_verb_form(cursor)
    if not verb_form:
        await message.answer("No hay datos para el juego.")
        conn.close()
        return

    verb_form_id, verb, tense, subject, form = verb_form
    game_text = f"Verbo: {verb}\nTiempo: {tense}\nSujeto: {subject}\nEscribe la forma correcta del verbo:"
    await message.answer(game_text) # , reply_markup=get_main_keyboard()

    await state.update_data(verb_form_id=verb_form_id, correct_form=form)
    await state.set_state(GameStates.waiting_for_answer)
    conn.close()


async def play_game(message: Message, state: FSMContext):
    await start_game(message, state)


async def check_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    correct_form = user_data.get("correct_form")
    
    user_input = message.text.strip()
    if user_input.lower() == correct_form.lower():
        await message.answer("¡Correcto!") # , reply_markup=get_main_keyboard()
    else:
        await message.answer(f"Incorrecto. La respuesta correcta es: {correct_form}") # , reply_markup=get_main_keyboard()

    # Запускаем новую игру
    await start_game(message, state)


async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="🚀 Iniciar bot"),
        types.BotCommand(command="/help", description="💡 Cómo funciona"),
        types.BotCommand(command="/play", description="🎯 Iniciar el juego"),
        types.BotCommand(command="/about", description="🦾 Sobre este bot"),
    ]
    await bot.set_my_commands(commands)


def register_handlers(dp: Dispatcher):
    dp.message.register(show_welcome, Command('start'))
    dp.message.register(show_help, Command('help'))
    dp.message.register(play_game, Command('play'))
    dp.message.register(show_about, Command('about')) #, lambda message: message["text"] == "🦾 Sobre este bot")
    dp.message.register(check_answer, GameStates.waiting_for_answer)
    dp.message.register(show_help)