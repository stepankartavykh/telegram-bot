from telebot.handler_backends import State, StatesGroup


class UserDialogLow(StatesGroup):
    """
    Состояние для команды /low
    Класс состояния пользователя для сохранения вводимой информации.
    city: город поиска
    date_in: дата заезда в отель
    date_out: дата выезда из отеля
    count_hotels: количество отелей, выводимых пользователю, для выбора
    count_photos: количество фотографий отеля, выводимых пользователю
    """
    city = State()
    date_in = State()
    date_out = State()
    count_hotels = State()
    count_photos = State()
