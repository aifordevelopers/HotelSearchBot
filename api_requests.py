import requests
from project.config import locations_url, properties_url, location_detail_url, headers


def location_request(location: str) -> str:
    querystring = {"q": location, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    response = requests.request("GET", locations_url, headers=headers, params=querystring)
    return response.text


def location_detail_request(id: str):
    payload = {"currency": "USD", "eapid": 1, "locale": "en_US", "siteId": 300000001, "propertyId": " ",
               'propertyId': id}
    response = requests.request("POST", location_detail_url, json=payload, headers=headers)
    return response.text


def property_request(user):
    """Запрос к АПИ на отели"""
    start_split = user.start_date.split('.')

    end_split = user.end_date.split('.')

    start_day: int = int(start_split[0])
    start_month: int = int(start_split[1])
    start_year: int = int(start_split[2])

    end_day: int = int(end_split[0])
    end_month: int = int(end_split[1])
    end_year: int = int(end_split[2])

    data = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {
            "regionId": 0
        },
        "checkInDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "checkOutDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "rooms": [
            {
                "adults": 2
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 0,
        "sort": "PRICE_LOW_TO_HIGH"
    }

    if not user.is_lowest:
        data['sort'] = 'PRICE_HIGH_TO_LOW'
    data['destination']['regionId'] = user.location_id

    data['checkInDate']['day'] = start_day
    data['checkInDate']['month'] = start_month
    data['checkInDate']['year'] = start_year

    data['checkOutDate']['day'] = end_day
    data['checkOutDate']['month'] = end_month
    data['checkOutDate']['year'] = end_year

    data['resultsSize'] = int(user.count)

    response = requests.request("POST", properties_url, json=data, headers=headers)
    return response.text


def best_deal_request(user):
    start_split = user.start_date.split('.')

    end_split = user.end_date.split('.')

    start_day: int = int(start_split[0])
    start_month: int = int(start_split[1])
    start_year: int = int(start_split[2])

    end_day: int = int(end_split[0])
    end_month: int = int(end_split[1])
    end_year: int = int(end_split[2])

    data = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {
            "regionId": 0
        },
        "checkInDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "checkOutDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "rooms": [
            {
                "adults": 2
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 0,
        "sort": "DISTANCE",
        "filters": {
            "price": {
                "max": 10000,
                "min": 100
            }
        }
    }

    if not user.is_lowest:
        data['sort'] = 'PRICE_HIGH_TO_LOW'
    data['destination']['regionId'] = user.location_id

    data['checkInDate']['day'] = start_day
    data['checkInDate']['month'] = start_month
    data['checkInDate']['year'] = start_year

    data['checkOutDate']['day'] = end_day
    data['checkOutDate']['month'] = end_month
    data['checkOutDate']['year'] = end_year

    data['resultsSize'] = int(user.count)

    data['filters']['price']['max'] = user.max_price
    data['filters']['price']['min'] = user.min_price

    response = requests.request("POST", properties_url, json=data, headers=headers)
    return response.text
