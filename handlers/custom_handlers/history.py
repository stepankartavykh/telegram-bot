from loader import db, bot
from telebot.types import Message
from states.dialog_state_history import UserDialogHistory
from database.history_database import Operations, Entry
from datetime import datetime
from loguru import logger


@bot.message_handler(commands=["history"])
def start_history_command(message: Message) -> None:
    """ Начало выполнения команды /history """
    Operations.add_entry(db, Entry("/history"))
    bot.send_message(message.chat.id, "Данная команда предоставит историю ваших запросов.")
    bot.send_message(message.chat.id, "Сколько последних записей хотите посмотреть? Укажите количество.")
    bot.set_state(message.from_user.id, UserDialogHistory.count_entries, message.chat.id)


@bot.message_handler(state=UserDialogHistory.count_entries)
@logger.catch
def custom_get_count_entries(message: Message) -> None:
    try:
        count = int(message.text)
        if count < 1:
            raise ValueError
        data = Operations.get_entries(db, count)
        message_to_bot = ""
        for element in data:
            _date = datetime.fromtimestamp(element[2]).strftime("-- %H:%M:%S - %d-%m-%Y --")
            message_to_bot += f"{element[1]}. Время вызова: {_date}\n"
        bot.send_message(message.chat.id, "История запросов.")
        bot.send_message(message.chat.id, message_to_bot)
        bot.delete_state(message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, "Должно быть натуральное число. Введите заново!")
