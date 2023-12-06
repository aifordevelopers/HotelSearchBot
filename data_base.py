import json
import os
from dataclasses import dataclass
from dataclasses_json import dataclass_json

"""
Данный файл описывает взаимодействие с базой данных (формат JSON).
"""

states = [
    'INSERT_LOCATION',
    'INSERT_COUNT',
    'INSERT_PHOTOS_NEEDED',
    'INSERT_PHOTOS_COUNT',
    'INSERT_START_DATE',
    'INSERT_END_DATE',
    'INSERT_END_DATE_BEST_DEAL',
    'INSERT_PRICE_RANGE'
    'INSERT_DISTANCE_RANGE'
]


@dataclass_json
@dataclass
class History:
    hotels = []
    datetime: str = ""
    command: str = ""


@dataclass_json
@dataclass
class User:
    telegram_id: str = ''
    state: str = ''
    location_id: str = ''
    count: int = 0
    photo_count: int = 0
    start_date: str = ''
    end_date: str = ''
    is_lowest: bool = True
    is_best_deal: bool = False
    min_price: int = 0
    max_price: int = 0
    max_distance: int = 0
    datetime: str = ""
    history = []


@dataclass_json
@dataclass
class Hotel:
    name: str = '',
    address: str = '',
    distance_from_centre: str = '',
    money: str = '',
    money_for_night: str = '',
    photo = []


def read_data(user_id: int) -> User:
    """Чтение вводимых данных пользователем из БД"""
    user = User(user_id, 'NONE')
    try:
        with open(os.path.join('database', str(user_id) + '.json'), 'r') as file:
            user_as_string = json.load(file)
            user = User.from_json(user_as_string)
    except FileNotFoundError:
        with open(os.path.join('database', str(user.telegram_id) + '.json'), 'w+') as file:
            data = user.to_json()
            json.dump(data, file, indent=4)
    return user


def write_data(user: User) -> None:
    """Запись данных пользователя в БД"""
    with open(os.path.join('database', str(user.telegram_id) + '.json'), 'w+') as file:
        data = user.to_json()
        json.dump(data, file, indent=4)
