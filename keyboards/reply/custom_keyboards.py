from typing import List
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

""" Клавиатура для подтверждения получения отелей (после получения всей информации) или выхода из команды. """
confirmation = InlineKeyboardMarkup()
confirmation.add(
    InlineKeyboardButton(text="Получить список отелей", callback_data="custom_confirmation_get_properties"),
    InlineKeyboardButton(text="Отмена. Выход из команды.", callback_data="quit_custom_command")
)


def get_keyboard_with_properties(hotels_required_info: List[tuple]) -> InlineKeyboardMarkup:
    """ Функция для получения клавиатуры отелей: -Имя отеля- -Цена- -Расстояние до центра локации- """
    required_hotels = InlineKeyboardMarkup()
    for index, element in enumerate(hotels_required_info):
        required_hotels.add(
            InlineKeyboardButton(text=f"{element[1]}", callback_data=f"{index}_custom_hotel"),
            InlineKeyboardButton(text=f"${round(element[2])}", callback_data="price_custom_button"),
            InlineKeyboardButton(text=f"{round(element[3], 3)}", callback_data="distance_custom_button"),
        )
    return required_hotels


""" Клавиатура для выхода из команды /custom """
abort_custom_command_keyboard = InlineKeyboardMarkup()
abort_custom_command_keyboard.add(
    InlineKeyboardButton(text="Отмена. Выход из команды.", callback_data="quit_custom_command")
)


""" Клавиатура для продолжения просмотра отелей. Либо выхода из поиска. """
quit_or_continue = InlineKeyboardMarkup()
yes = InlineKeyboardButton(text="Да", callback_data="continue_custom_search")
no = InlineKeyboardButton(text="Нет", callback_data="break_custom_search")
quit_or_continue.row(yes, no)
