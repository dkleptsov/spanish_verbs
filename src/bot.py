import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from bot_handlers import register_handlers, set_bot_commands

API_TOKEN = os.getenv("VERBOS_ESP_TEST_BOT")

if not API_TOKEN:
    raise ValueError("API_TOKEN no está establecido o no es válido.")

logging.basicConfig(level=logging.INFO)

# Inicializar bot y despachador
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)

# Registro de controladores
register_handlers(dp)

# Registro de comandos de bot al inicio
@dp.startup()
async def on_startup():
    await set_bot_commands(bot)

if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=False)
