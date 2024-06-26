import logging
import sqlite3
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils import executor

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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

@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer("¡Bienvenido al juego de los verbos en español!\nEscribe /play para empezar a jugar.")

@dp.message(Command('play'))
async def play_game(message: Message):
    db_name = 'verbs.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    verb_form = get_random_verb_form(cursor)
    if not verb_form:
        await message.answer("No hay datos para el juego.")
        conn.close()
        return

    verb_form_id, verb, tense, subject, form = verb_form
    await message.answer(f"Género: {verb}\nTiempo: {tense}\nSujeto: {subject}\nEscribe la forma correcta del verbo:")

    state = dp.current_state(user=message.from_user.id)
    await state.set_state("waiting_for_answer")
    await state.update_data(verb_form_id=verb_form_id, correct_form=form)
    conn.close()

@dp.message(state="waiting_for_answer")
async def check_answer(message: Message, state):
    user_data = await state.get_data()
    correct_form = user_data.get("correct_form")
    
    user_input = message.text.strip()
    if user_input.lower() == correct_form.lower():
        await message.answer("¡Correcto!")
    else:
        await message.answer(f"Incorrecto. La respuesta correcta es: {correct_form}")

    await state.reset_state()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
