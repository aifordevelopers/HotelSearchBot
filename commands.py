from datetime import datetime
from project import data_base, api_requests
from telebot import types
import json
import re
from project.data_base import User, Hotel


def handle_first_request(user: User, message: types.Message, is_lowest: bool, is_best_deal: bool) -> str:
    """Запрос у пользователя искомого города"""
    user.state = 'INSERT_LOCATION'
    user.datetime = str(datetime.now())
    user.is_lowest = is_lowest
    user.is_best_deal = is_best_deal
    data_base.write_data(user)
    return 'Введите город (en)'


def handle_city_insert(message: types.Message, user: User) -> str:
    """Обработка запроса пользователя по поиску города, запрос значения количества отелей"""
    response = api_requests.location_request(message.text)
    try:
        location_id = json.loads(response)['sr'][0]['gaiaId']
    except:
        return "Нет такого города, введите другой (en)"
    user.state = 'INSERT_COUNT'
    user.location_id = location_id
    data_base.write_data(user)
    return f"Сколько отелей Вам показать?"


def handle_count_insert(message: types.Message, user) -> str:
    """Обработка значения количества отелей пользователя, запрос необходимости вывода фото"""
    if 1 <= int(message.text) <= 10:
        user.count = message.text
        user.state = 'INSERT_PHOTOS_NEEDED'
        data_base.write_data(user)
        return f"Загрузить фотографий для каждого отеля (“Да/Нет”)?"
    return f"Введите число меньше 10"


def handle_photos_needed(message: types.Message, user) -> str:
    """Обработка ответа пользователя о необходимости вывода фото, запрос стартовой даты."""
    text = message.text.lower()
    if text == 'нет':
        user.state = 'INSERT_START_DATE'
        data_base.write_data(user)
        return f"Введите дату начала в формате 31.01.2023"
    elif text == 'да':
        user.state = 'INSERT_PHOTOS_COUNT'
        data_base.write_data(user)
        return f"Введите количество фото (не больше 5)"
    else:
        return f"Загрузить фотографий для каждого отеля? (Введите Да/Нет)"


def handle_photos_count(message, user):
    """Обработка значения количества фото, запрос стартовой даты"""
    if 1 <= int(message.text) <= 5:
        user.photo_count = message.text
        user.state = 'INSERT_START_DATE'
        data_base.write_data(user)
        return f"Введите дату начала в формате 31.01.2023"
    return f"Введите число меньше или равное 5"


def handle_insert_start_date(message: types.Message, user):
    """Обработка ввода стартовой даты, запрос конечной даты"""
    pattern = re.compile("\d{2}\.\d{2}\.\d{4}")
    if pattern.match(message.text):
        if user.is_best_deal:
            return handle_start_date_best_deal(message, user)
        user.state = 'INSERT_END_DATE'
        user.start_date = message.text
        data_base.write_data(user)
        return "Введите дату конца в формате 31.01.2023"
    else:
        return "Введите дату начала в формате 31.01.2023"


def handle_insert_end_date(message, user):
    """Обработка ввода конечной даты, выполнение поиска вариантов, представление результатов"""
    pattern = re.compile("\d{2}\.\d{2}\.\d{4}")
    if not pattern.match(message.text):
        return "Введите дату конца в формате 31.01.2023"
    user.end_date = message.text
    data_base.write_data(user)
    response = api_requests.property_request(user)
    hotels_json = json.loads(response)
    if hotels_json['data'] is None:
        return "Не существует отелей с такими параметрами"
    properties = json.loads(response)['data']['propertySearch']['properties']
    hotel_info_list = []
    for p in properties:
        name = p['name']
        distance_from_center = str(str(p['destinationInfo']['distanceFromDestination']['value']) + ' ' +
                                   p['destinationInfo']['distanceFromDestination']['unit'])
        price = p['price']['options'][0]['formattedDisplayPrice']
        price_total = p['price']['displayMessages'][1]['lineItems'][0]['value']
        hotel_info_json = json.loads(api_requests.location_detail_request(p['id']))
        address = hotel_info_json['data']['propertyInfo']['summary']['location']['address']['addressLine']
        photo_urls = []
        for i in range(int(user.photo_count)):
            photo_url = hotel_info_json['data']['propertyInfo']['propertyGallery']['images'][i]['image']['url']
            photo_urls.append(photo_url)

        hotel = Hotel(name, address, distance_from_center, price_total, price)
        hotel.photo = photo_urls
        hotel_info_list.append(hotel)
    return hotel_info_list


def handle_start_date_best_deal(message, user):
    """Обработка стартовой даты, запрос конечной даты для команды bestdeal"""
    pattern = re.compile("\d{2}\.\d{2}\.\d{4}")
    if pattern.match(message.text):
        user.state = 'INSERT_END_DATE_BEST_DEAL'
        user.start_date = message.text
        data_base.write_data(user)
        return "Введите дату конца в формате 31.01.2023"
    else:
        return "Введите дату начала в формате 31.01.2023"


def handle_end_date_best_deal(message, user):
    """Обработка конечной даты, запрос диапазона цен для команды bestdeal"""
    pattern = re.compile("\d{2}\.\d{2}\.\d{4}")
    if pattern.match(message.text):
        user.state = 'INSERT_PRICE_RANGE'
        user.end_date = message.text
        data_base.write_data(user)
        return "Введите диапазон цен в формате 100-500 (в $)"
    else:
        return "Введите дату начала в формате 31.01.2023"


def handle_price_range(message, user):
    """Обработка диапазона цен, запрос расстояния от центра для команды bestdeal"""
    pattern = re.compile("\d+-\d+")
    if pattern.match(message.text):
        split = message.text.split("-")
        min = int(split[0])
        max = int(split[1])
        if int(min) >= int(max):
            return "Введите диапазон цен за ночь в формате 100-500 (в $)"
        user.min_price = min
        user.max_price = max
        user.state = 'INSERT_DISTANCE_RANGE'
        data_base.write_data(user)
        return "Введите расстояние(мили) от отеля до центра (целое число)"
    else:
        "Введите диапазон цен за ночь в формате 100-500 (в $)"


def handle_distance_range(message, user):
    """Обработка расстояния от центра, , выполнение поиска вариантов, представление результатов для команды bestdeal"""
    pattern = re.compile("\d+")
    if not pattern.match(message.text):
        return "Введите расстояние(мили) от отеля до центра (целое число)"
    distance = message.text
    user.max_distance = int(distance)
    data_base.write_data(user)
    response = api_requests.best_deal_request(user)
    hotels_json = json.loads(response)
    if hotels_json['data'] is None:
        return "Не существует отелей с такими параметрами"
    properties = hotels_json['data']['propertySearch']['properties']
    hotel_info_list = []
    for p in properties:
        name = p['name']
        hotel_distance = p['destinationInfo']['distanceFromDestination']['value']
        if float(hotel_distance) > float(distance):
            continue
        distance_from_center = str(str(hotel_distance) + ' ' +
                                   p['destinationInfo']['distanceFromDestination']['unit'])
        price = p['price']['options'][0]['formattedDisplayPrice']
        price_total = p['price']['displayMessages'][1]['lineItems'][0]['value']
        hotel_info_json = json.loads(api_requests.location_detail_request(p['id']))
        address = hotel_info_json['data']['propertyInfo']['summary']['location']['address']['addressLine']
        photo_urls = []
        for i in range(int(user.photo_count)):
            photo_url = hotel_info_json['data']['propertyInfo']['propertyGallery']['images'][i]['image']['url']
            photo_urls.append(photo_url)
        hotel = Hotel(name, address, distance_from_center, price_total, price)
        hotel.photo = photo_urls
        hotel_info_list.append(hotel)
    return hotel_info_list
