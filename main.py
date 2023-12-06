import telebot
from project import commands
import data_base
from telebot import types
from project.config import bot


@bot.message_handler(commands=['start'])
def start(message=None):
    """Приветственное сообщение"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id,
                     "👋 Привет! Я бот-помощник, который подберет тебе самый подходящий отель!",
                     reply_markup=markup)


def get_photos(photo):
    """Формирование списка фотографий"""
    result = []
    for p in photo:
        result.append(types.InputMediaPhoto(media=p))
    return result


@bot.message_handler(content_types=['text'])
def get_text_messages(message: types.Message):
    """Обработка данных выбранной команды(кнопки), определение следующего шага обработчика"""
    user = data_base.read_data(message.chat.id)
    if user.state == 'INSERT_LOCATION':
        response = commands.handle_city_insert(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_COUNT':
        response = commands.handle_count_insert(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_PHOTOS_NEEDED':
        response = commands.handle_photos_needed(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_PHOTOS_COUNT':
        response = commands.handle_photos_count(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_START_DATE':
        response = commands.handle_insert_start_date(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_END_DATE':
        response = commands.handle_insert_end_date(message, user)

        for p in response:
            bot.send_message(chat_id=message.chat.id, text=get_message_from_hotel_info_list(p))
            if len(p.photo) == 0:
                continue
            bot.send_media_group(chat_id=message.chat.id, media=get_photos(p.photo))
        user.history.append(get_history(user, response))
        create_start_response(message)
        user.state = ""
        data_base.write_data(user)

    elif user.state == 'INSERT_END_DATE_BEST_DEAL':
        response = commands.handle_end_date_best_deal(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_PRICE_RANGE':
        response = commands.handle_price_range(message, user)
        bot.send_message(chat_id=message.chat.id, text=response)

    elif user.state == 'INSERT_DISTANCE_RANGE':
        response = commands.handle_distance_range(message, user)
        if isinstance(response, str):
            bot.send_message(chat_id=message.chat.id, text=response)
            if response == "Не существует отелей с такими параметрами":
                create_start_response(message)
                user.state = ""
                data_base.write_data(user)
            return
        for p in response:
            bot.send_message(chat_id=message.chat.id, text=get_message_from_hotel_info_list(p))
            if len(p.photo) == 0:
                continue
            bot.send_media_group(chat_id=message.chat.id, media=get_photos(p.photo))
        user.history.append(get_history(user, response))
        create_start_response(message)
        user.state = ""
        data_base.write_data(user)

    elif message.text == '👋 Поздороваться':
        create_start_response(message)

    elif message.text == 'lowprice':
        bot.send_message(chat_id=message.chat.id, text=commands.handle_first_request(user, message, True, False))

    elif message.text == 'highprice':
        bot.send_message(chat_id=message.chat.id, text=commands.handle_first_request(user, message, False, False))

    elif message.text == 'bestdeal':
        bot.send_message(chat_id=message.chat.id, text=commands.handle_first_request(user, message, False, True))

    elif message.text == 'history':
        if len(user.history) == 0:
            bot.send_message(chat_id=message.chat.id, text="История пустая")
        else:
            for entry in user.history:
                bot.send_message(chat_id=message.chat.id,
                                 text="Критерий поиска: " + entry.command + "\nВремя: " + entry.datetime)
                for p in entry.hotels:
                    bot.send_message(chat_id=message.chat.id, text=get_message_from_hotel_info_list(p))
                    if len(p.photo) == 0:
                        continue
                    bot.send_media_group(chat_id=message.chat.id, media=get_photos(p.photo))

    elif message.text == 'help':
        bot.send_message(message.from_user.id, 'Ты можешь выбрать город, дату, желаемый диапазон цен($),\
         а также, если захочешь, я могу найти для тебя фотографии отелей!\
        ❓Как пользоваться❓\n\
        👉 lowprice - поиск самых дешевых отелей\n\
        👉 highprice - поиск дорогих отелей\n\
        👉 bestdeal - поиск лучших предложений\n\
        👉 history - история поиска')


def create_start_response(message):
    """Создание кнопок, которые отвечают за возможности бота
    Отправка пользователю сообщения с выбором действия."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('lowprice')
    btn2 = types.KeyboardButton('highprice')
    btn3 = types.KeyboardButton('bestdeal')
    btn4 = types.KeyboardButton('history')
    btn5 = types.KeyboardButton('help')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.from_user.id, '❓Выберите действие ❓', reply_markup=markup)


def get_message_from_hotel_info_list(h):
    """Итоговый вывод для пользователя"""
    hotel = str('Я нашёл следующие варианты:\n\
    🏛Название отеля: {}\n\
    🌎Адрес: {}\n\
    🌎Расстояние до центра: {}\n\
    💸Стоимость за весь срок: {}\n\
    💸Стоимость за ночь: {}') \
        .format(h.name, h.address, h.distance_from_centre, h.money, h.money_for_night)
    return hotel


def get_history(user, hotels):
    """Функция для записи истории"""
    command: str
    if user.is_best_deal:
        command = "bestdeal"
    else:
        if user.is_lowest:
            command = "lowprice"
        else:
            command = "highprice"
    history = data_base.History()
    history.hotels = hotels
    history.datetime = user.datetime
    history.command = command
    return history


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
