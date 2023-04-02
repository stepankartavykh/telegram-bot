from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from database.history_database import DatabaseAndTableCreate


db = DatabaseAndTableCreate("database/db_history.sqlite")
db.create_table_history()

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
