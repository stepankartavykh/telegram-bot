from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot, db
from database.history_database import Operations, Entry


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """ Обработка команды /help """
    Operations.add_entry(db, Entry("/help"))
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id, "\n".join(text))
