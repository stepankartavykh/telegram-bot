from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from telebot import TeleBot


def set_default_commands(bot: TeleBot) -> None:
    """ Установка доступных команд """
    bot.set_my_commands(
        [BotCommand(*command) for command in DEFAULT_COMMANDS]
    )
