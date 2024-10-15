""" Main script that initializes and runs the Telegram bot. """

import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from bot_handlers import register_handlers, set_bot_commands

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the bot token from the environment variable
API_TOKEN = os.getenv("SPANISH_VERBS_BOT")

# Check if the API token is valid
if not API_TOKEN:
    raise ValueError("API_TOKEN is not set or is invalid.")

# Initialize the bot and dispatcher
bot: Bot = Bot(token=API_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)

# Register handlers
register_handlers(dp)

@dp.startup()
async def on_startup() -> None:
    """Startup actions for the bot."""
    await set_bot_commands(bot)

if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=False)
