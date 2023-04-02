from telebot.types import Message
from loader import bot, db
from database.history_database import Operations, Entry


@bot.message_handler(commands=["start"])
def bot_start(message: Message) -> None:
    """ Обработка начала взаимодействия с ботом """
    Operations.add_entry(db, Entry("/start"))
    bot.send_message(message.chat.id, f"Привет, {message.from_user.full_name}! Вас приветствует бот по поиску отеля.")
