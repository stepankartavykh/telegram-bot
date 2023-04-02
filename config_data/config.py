""" Файл с токенами к боту и к используемым API, а также список доступных команд бота """

import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку по командам"),
    ("low", "Вывод самых доступных по цене отелей"),
    ("high", "Вывод самых дорогих по цене отелей"),
    ("custom", "Поиск по параметрам"),
    ("history", "История запросов"),
)
