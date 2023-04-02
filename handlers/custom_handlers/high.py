from telebot.types import Message, CallbackQuery, InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot, db
from config_data import config
from states.dialog_state_high import UserDialogHigh
from API.request_locations import get_locations
from API.request_properties import get_properties
from API.request_details import get_details
from keyboards.reply import high_keyboards
from database.history_database import Entry, Operations
import datetime
import locale

PERIODS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def high_get_required_parameters(property_parameters: dict) -> tuple:
    """ Функция для получения параметров из properties. Возвращает AttributeError при отсутствии параметра. """
    prop_id = property_parameters.get("id")
    prop_name = property_parameters.get("name")
    prop_price = property_parameters.get("price").get("options")[0].get("strikeOut").get("amount")
    return prop_id, prop_name, prop_price


@bot.message_handler(commands=["high"])
def high_command_start(message: Message) -> None:
    """ Обработка команды /low """
    Operations.add_entry(db, Entry("/high"))
    bot.send_message(message.chat.id, "Данная команда предоставит информацию о самых дорогих отелях.")
    bot.send_message(message.chat.id, "Введите город для поиска:")
    bot.set_state(message.from_user.id, UserDialogHigh.city, message.chat.id)


@bot.message_handler(state=UserDialogHigh.city)
def high_get_city_and_ask_for_date_check_in(message: Message) -> None:
    """ Функция для записи города в data и вывод календаря для получения даты въезда. """
    city = message.text
    city = city[0].upper() + city[1:]
    city_locations = get_locations(config.RAPID_API_KEY, city)
    for location in city_locations:
        if location["regionNames"]["shortName"] == city:
            location_id = location['gaiaId']
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data["city"] = city
                data['location_id'] = location_id
            bot.send_message(message.chat.id, "Введи дату въезда:")
            calendar_date_in, step_in = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=2,
                                                                 locale='ru').build()
            bot.send_message(message.chat.id, f"Выбери {PERIODS[step_in]}", reply_markup=calendar_date_in)
            break
    else:
        bot.send_message(message.chat.id, "Такого города не найдено. Введите заново!")


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def high_get_date_in_and_ask_for_date_check_out(call_in: CallbackQuery) -> None:
    """ Функция для обработки даты заезда. Идет запись даты в data. Вывод календаря для получения даты выезда. """
    result, key, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=2, locale='ru').process(
        call_in.data)
    if not result and key:
        bot.edit_message_text(
            f"Выберите {PERIODS[step]}",
            call_in.message.chat.id,
            call_in.message.message_id,
            reply_markup=key
        )
    elif result:
        year, month, day = str(result).split('-')
        date_check_in = datetime.date(int(year), int(month), int(day))
        locale.setlocale(locale.LC_ALL, "")
        result = date_check_in.strftime("%d %B %Y (%A)")
        bot.edit_message_text(
            f"Дата заезда {result}",
            call_in.message.chat.id,
            call_in.message.message_id
        )
        with bot.retrieve_data(user_id=call_in.from_user.id, chat_id=call_in.message.chat.id) as data:
            data["day_in"] = day
            data["month_in"] = month
            data["year_in"] = year
        calendar_date_out, step_out = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=3,
                                                               locale='ru').build()
        bot.send_message(call_in.message.chat.id, "Теперь дата выезда:")
        bot.send_message(call_in.message.chat.id, f"Выбери {PERIODS[step_out]}", reply_markup=calendar_date_out)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def high_get_date_out_and_ask_count_hotels(call_out: CallbackQuery) -> None:
    """ Функция для обработки даты выезда. Идет запись даты в data. Запрос на получение количества вариантов отелей. """
    with bot.retrieve_data(user_id=call_out.from_user.id, chat_id=call_out.message.chat.id) as data:
        day_in, month_in, year_in = int(data["day_in"]), int(data["month_in"]), int(data["year_in"])
    date_out_low_limit = datetime.date(year_in, month_in, day_in) + datetime.timedelta(days=1)
    result, key, step = DetailedTelegramCalendar(min_date=date_out_low_limit, calendar_id=3, locale='ru').process(
        call_out.data)
    if not result and key:
        bot.edit_message_text(
            f"Выберите {PERIODS[step]}",
            call_out.message.chat.id,
            call_out.message.message_id,
            reply_markup=key
        )
    elif result:
        year, month, day = str(result).split('-')
        date_check_in = datetime.date(int(year), int(month), int(day))
        result = date_check_in.strftime("%d %B %Y (%A)")
        bot.edit_message_text(
            f"Дата заезда {result}",
            call_out.message.chat.id,
            call_out.message.message_id
        )
        with bot.retrieve_data(user_id=call_out.from_user.id, chat_id=call_out.message.chat.id) as data:
            data["day_out"] = day
            data["month_out"] = month
            data["year_out"] = year
        bot.send_message(call_out.message.chat.id, "Сколько вариантов отелей хотите посмотреть?")
        bot.set_state(call_out.from_user.id, UserDialogHigh.count_hotels, call_out.message.chat.id)


@bot.message_handler(state=UserDialogHigh.count_hotels)
def high_limit_output_entries(message: Message) -> None:
    """ Запись количества выводимых отелей. Запрос на получение количества фотографий для показа пользователю. """
    try:
        limit = int(message.text)
        if limit < 0:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if len(data.values()) == 0:
                return None
            data["count_hotels"] = limit
        bot.send_message(message.chat.id, "Сколько фотографий одного отеля вам показывать?")
        bot.set_state(message.from_user.id, UserDialogHigh.count_photos, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный ввод количества выводимых отелей. Введите заново:")


@bot.message_handler(state=UserDialogHigh.count_photos)
def high_get_count_hotels_and_ask_confirmation(message: Message):
    """ Запись количества фотографий одного отеля. Подтверждение вывода списка отелей и цен. """
    try:
        photos_limit = int(message.text)
        if photos_limit < 1:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if len(data.values()) == 0:
                return None
            data["limit_photos"] = photos_limit
        bot.send_message(message.chat.id, "Подтвердите выполнение запроса.", reply_markup=high_keyboards.confirmation)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный ввод количества фотографий одного отеля! Введите заново:")


@bot.callback_query_handler(func=lambda call: call.data == "quit_high_command")
def high_quit_command(call: CallbackQuery) -> None:
    """ Обработка выхода из команды /high. Удаляется состояние пользователя. """
    bot.send_message(call.message.chat.id, "Осуществлен выход из команды high.")
    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "get_hotels_list_high")
def high_get_properties_from_api(call: CallbackQuery) -> None:
    """ Формирование запроса к API на получение вариантов отелей и их цен. Вывод названий отелей и их цен кнопками. """
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        day_in = int(data["day_in"])
        month_in = int(data["month_in"])
        year_in = int(data["year_in"])
        day_out = int(data["day_out"])
        month_out = int(data["month_out"])
        year_out = int(data["year_out"])
        id_location_to_find = data["location_id"]
        limit = data["count_hotels"]
    properties = get_properties(config.RAPID_API_KEY, id_location_to_find, day_in, month_in, year_in, day_out,
                                month_out, year_out)
    properties = properties["data"]["propertySearch"]["properties"]
    names_prices = []
    count_properties_with_missing_parameters = 0
    for item_property in properties:
        try:
            property_id, property_name, data_price = high_get_required_parameters(item_property)
            names_prices.append((property_id, property_name, float(data_price)))
        except AttributeError:
            count_properties_with_missing_parameters += 1
    if len(names_prices) == 0:
        bot.send_message(call.message.chat.id, "Подходящих отелей нет.")
        high_quit_command(call)
        return None
    names_prices = sorted(names_prices, key=lambda elem: elem[2], reverse=True)[:limit]
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data["list_shown_hotels"] = names_prices
        data["hotels_list_keyboard"] = high_keyboards.get_keyboard_with_properties(names_prices)
    bot.send_message(call.message.chat.id, "Список отелей:",
                     reply_markup=high_keyboards.get_keyboard_with_properties(names_prices))
    bot.send_message(
        call.message.chat.id,
        "Если хотите увидеть фотографии отеля, нажмите на кнопку с названием.",
        reply_markup=high_keyboards.abort_high_command_keyboard
    )


@bot.callback_query_handler(func=lambda call: "shown_hotel_buttonHigh" in call.data)
def high_get_property_details_from_api(call: CallbackQuery) -> None:
    """ Функция для формирования запроса к API для получения подробной информации об отеле """
    hotel_index = int(call.data[:call.data.index('_')])
    this_hotel_already_shown = False
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        if "shown_hotels" in data.keys():
            if hotel_index in data["shown_hotels"]:
                this_hotel_already_shown = True
            else:
                data["shown_hotels"].append(hotel_index)
        else:
            data["shown_hotels"] = [hotel_index]
        buttons_data = data["list_shown_hotels"]
        limit_photos_count = data["limit_photos"]
    if not this_hotel_already_shown:
        required_id = buttons_data[hotel_index][0]
        details = get_details(config.RAPID_API_KEY, required_id)
        images = details["data"]["propertyInfo"]["propertyGallery"]["images"]
        photos = []
        for image in images[:limit_photos_count]:
            photos.append(InputMediaPhoto(media=image["image"]["url"]))
        bot.send_media_group(call.message.chat.id, photos)
        bot.send_message(call.message.chat.id, "Будете дальше смотреть отели?",
                         reply_markup=high_keyboards.quit_or_continue)
    else:
        bot.send_message(call.message.chat.id, "Вы уже просмотрели фотографии данного отеля.")


@bot.callback_query_handler(func=lambda call: call.data == "continue_search_high")
def high_continue_search(call: CallbackQuery) -> None:
    """ Обработчик продолжения показа найденных отелей. """
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        hotels = data["hotels_list_keyboard"]
    bot.send_message(call.message.chat.id, "Выбирайте отель для просмотра:", reply_markup=hotels)


@bot.callback_query_handler(func=lambda call: call.data == "break_search_high")
def high_break_search(call: CallbackQuery) -> None:
    """ Завершение команды /high. """
    bot.send_message(call.message.chat.id, "Поиск завершен!")
    bot.delete_state(call.from_user.id)
