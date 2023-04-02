from telebot.handler_backends import State, StatesGroup


class UserDialogHistory(StatesGroup):
    """
    Состояние для команды /low
    :count_entries: Число выводимых записей истории запросов.
    """
    count_entries = State()
