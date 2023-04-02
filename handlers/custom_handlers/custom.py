from telebot.types import Message, CallbackQuery, InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot, db
from config_data import config
from states.dialog_state_custom import UserDialogCustom
from API.request_locations import get_locations
from API.request_properties import get_properties_custom
from API.request_details import get_details
from database.history_database import Entry, Operations
from keyboards.reply import custom_keyboards
import datetime
import locale
from loguru import logger

PERIODS = {'y': 'год', 'm': 'месяц', 'd': 'день'}
COEFFICIENT_MILES_TO_KM = 1.60934


def custom_get_required_parameters(property_parameters: dict, max_distance: int) -> tuple:
    """ Функция для получения параметров из properties. Возвращает AttributeError при отсутствии параметра, а также при
    превышении максимального расстояния от отеля до центра города. """
    prop_id = property_parameters.get("id")
    prop_name = property_parameters.get("name")
    prop_price = property_parameters.get("price").get("options")[0].get("strikeOut").get("amount")
    prop_distance_to_center = property_parameters.get("destinationInfo").get("distanceFromDestination").get(
        "value") * COEFFICIENT_MILES_TO_KM
    if prop_distance_to_center > max_distance:
        raise AttributeError
    return prop_id, prop_name, prop_price, prop_distance_to_center


@bot.message_handler(commands=["custom"])
def custom_command_start(message: Message) -> None:
    """ Обработка команды /custom """
    Operations.add_entry(db, Entry("/custom"))
    bot.send_message(message.chat.id, "Данная команда предоставит информацию об отелях с дополнительными параметрами.")
    bot.send_message(message.chat.id, "Введите город для поиска:")
    bot.set_state(message.from_user.id, UserDialogCustom.city, message.chat.id)


@bot.message_handler(state=UserDialogCustom.city)
def custom_get_city(message: Message) -> None:
    """ Функция для записи города в data и вывода календаря для ввода даты заезда """
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
            calendar_date_in, step_in = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=4,
                                                                 locale='ru').build()
            bot.send_message(message.chat.id, f"Выбери {PERIODS[step_in]}", reply_markup=calendar_date_in)
            break
    else:
        bot.send_message(message.chat.id, "Такого города не найдено. Введите заново!")


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
@logger.catch
def custom_calendar_date_in_handler(call_in: CallbackQuery) -> None:
    """ Функция для обработки даты заезда. Идет запись даты в data. Запрос даты выезда. """
    result, key, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=4, locale='ru').process(
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
        calendar_date_out, step_out = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=5,
                                                               locale='ru').build()
        bot.send_message(call_in.message.chat.id, "Теперь дата выезда:")
        bot.send_message(call_in.message.chat.id, f"Выбери {PERIODS[step_out]}", reply_markup=calendar_date_out)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
@logger.catch
def custom_calendar_date_out_handler(call_out: CallbackQuery) -> None:
    """ Функция для обработки даты выезда. Идет запись даты в data. Запрос количества выводимых отелей. """
    with bot.retrieve_data(user_id=call_out.from_user.id, chat_id=call_out.message.chat.id) as data:
        day_in, month_in, year_in = int(data["day_in"]), int(data["month_in"]), int(data["year_in"])
    date_out_low_limit = datetime.date(year_in, month_in, day_in) + datetime.timedelta(days=1)
    result, key, step = DetailedTelegramCalendar(min_date=date_out_low_limit, calendar_id=5, locale='ru').process(
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
            f"Дата выезда {result}",
            call_out.message.chat.id,
            call_out.message.message_id
        )
        with bot.retrieve_data(user_id=call_out.from_user.id, chat_id=call_out.message.chat.id) as data:
            data["day_out"] = day
            data["month_out"] = month
            data["year_out"] = year
        bot.send_message(call_out.message.chat.id, "Сколько вариантов отелей хотите посмотреть?")
        bot.set_state(call_out.from_user.id, UserDialogCustom.count_hotels, call_out.message.chat.id)


@bot.message_handler(state=UserDialogCustom.count_hotels)
def custom_limit_output_entries(message: Message) -> None:
    """ Запись количества выводимых отелей. Запрос на получение количества фотографий для показа пользователю. """
    try:
        limit = int(message.text)
        if limit < 0:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as saved_values:
            if len(saved_values.values()) == 0:
                return None
            saved_values["count_hotels"] = limit
        bot.send_message(message.chat.id, "Сколько фотографий одного отеля вам показывать?")
        bot.set_state(message.from_user.id, UserDialogCustom.count_photos, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный ввод количества выводимых отелей. Введите заново:")


@bot.message_handler(state=UserDialogCustom.count_photos)
def custom_count_photos_for_hotel(message: Message) -> None:
    """ Запись количества фотографий одного отеля. Подтверждение вывода списка отелей и цен. """
    try:
        photos_limit = int(message.text)
        if photos_limit < 1:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if len(data.values()) == 0:
                return None
            data["limit_photos"] = photos_limit
        bot.send_message(message.chat.id, "Укажите нижнюю границу цены(в долларах) за отель.")
        bot.set_state(message.from_user.id, UserDialogCustom.price_from, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный ввод количества фотографий одного отеля! Введите заново:")


@bot.message_handler(state=UserDialogCustom.price_from)
def custom_get_price_from(message: Message) -> None:
    """ Получение нижнего предела цены для поиска. """
    try:
        price_from = int(message.text)
        if price_from < 0:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as saved_values:
            saved_values["price_from"] = price_from
        bot.send_message(message.chat.id, "Укажите верхнюю границу цены(в долларах) за отель.")
        bot.set_state(message.from_user.id, UserDialogCustom.price_to, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный ввод нижней цены! Введите заново:")


@bot.message_handler(state=UserDialogCustom.price_to)
def custom_get_price_to(message: Message) -> None:
    """ Получение нижнего предела цены для поиска. """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as saved_values:
            price_to = int(message.text)
            if price_to < 0 or saved_values["price_from"] >= price_to:
                raise ValueError
            saved_values["price_to"] = price_to
        bot.send_message(message.chat.id, "Укажите максимально допустимое расстояние от центра до отеля, в километрах.")
        bot.set_state(message.from_user.id, UserDialogCustom.max_distance_from_centre, message.chat.id)
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод верхней цены! Верхняя цена должна быть > 0 и больше нижней цены. Введите заново:"
        )


@bot.message_handler(state=UserDialogCustom.max_distance_from_centre)
def custom_get_distance_from_centre(message: Message) -> None:
    """ Запись максимального расстояния от центра до отеля. Получение подтверждения на выполнение запроса. """
    try:
        distance = float(message.text)
        if distance <= 0 or distance > 100:
            raise ValueError
        with bot.retrieve_data(message.from_user.id, message.chat.id) as saved_values:
            saved_values["max_distance_from_centre"] = distance
        bot.send_message(message.chat.id, "Подтвердите выполнение запроса.", reply_markup=custom_keyboards.confirmation)
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод максимальной дистанции до центра. Заново введите!"
        )


@bot.callback_query_handler(func=lambda call: call.data == "custom_confirmation_get_properties")
@logger.catch
def custom_get_properties(call: CallbackQuery) -> None:
    """ Формирование запроса к API на получение вариантов отелей и их цен, расстояния. Вывод кнопками. """
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        day_in = int(data["day_in"])
        month_in = int(data["month_in"])
        year_in = int(data["year_in"])
        day_out = int(data["day_out"])
        month_out = int(data["month_out"])
        year_out = int(data["year_out"])
        id_location_to_find = data["location_id"]
        limit_hotels = data["count_hotels"]
        price_min = data["price_from"]
        price_max = data["price_to"]
        max_distance = data["max_distance_from_centre"]
    properties = get_properties_custom(
        config.RAPID_API_KEY, id_location_to_find,
        day_in, month_in, year_in,
        day_out, month_out, year_out,
        price_min=price_min, price_max=price_max
    )
    properties = properties["data"]["propertySearch"]["properties"]
    names_prices = []
    count_properties_with_missing_parameters = 0
    for item_property in properties:
        try:
            property_id, property_name, data_price, distance_to_center = custom_get_required_parameters(item_property,
                                                                                                        max_distance)
            names_prices.append((property_id, property_name, float(data_price), distance_to_center))
        except AttributeError:
            count_properties_with_missing_parameters += 1
    if len(names_prices) == 0:
        bot.send_message(call.message.chat.id, "Подходящих отелей нет.")
        custom_quit_command(call)
        return None
    names_prices = sorted(names_prices, key=lambda elem: elem[3])[:limit_hotels]
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data["list_shown_hotels"] = names_prices
        data["hotels_list_keyboard"] = custom_keyboards.get_keyboard_with_properties(names_prices)
    bot.send_message(
        call.message.chat.id,
        "Список отелей, отсортированных по расстоянию до центра:",
        reply_markup=custom_keyboards.get_keyboard_with_properties(names_prices)
    )
    bot.send_message(
        call.message.chat.id,
        "Если хотите увидеть фотографии отеля, нажмите на кнопку с названием.",
        reply_markup=custom_keyboards.abort_custom_command_keyboard
    )


@bot.callback_query_handler(func=lambda call: "_custom_hotel" in call.data)
@logger.catch
def custom_get_property_details_from_api(call: CallbackQuery) -> None:
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
                         reply_markup=custom_keyboards.quit_or_continue)
    else:
        bot.send_message(call.message.chat.id, "Вы уже просмотрели фотографии данного отеля.")


@bot.callback_query_handler(func=lambda call: call.data == "continue_custom_search")
def custom_continue_search_hotel(call: CallbackQuery) -> None:
    """ Обработчик продолжения показа найденных отелей. """
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        hotels = data["hotels_list_keyboard"]
    bot.send_message(call.message.chat.id, "Выбирайте отель для просмотра:", reply_markup=hotels)


@bot.callback_query_handler(func=lambda call: call.data == "break_custom_search")
def custom_break_search(call: CallbackQuery) -> None:
    """ Завершение команды /low. """
    bot.send_message(call.message.chat.id, "Поиск завершен!")
    bot.delete_state(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == "quit_custom_command")
def custom_quit_command(call: CallbackQuery) -> None:
    """ Обработка выхода из команды /custom. Удаляется состояние пользователя. """
    bot.send_message(call.message.chat.id, "Осуществлен выход из команды custom.")
    bot.delete_state(call.from_user.id)
