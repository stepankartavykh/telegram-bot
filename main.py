from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands
from telebot.custom_filters import StateFilter
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 KB", serialize=True)


@logger.catch
def start_bot():
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    start_bot()
