import telebot

bot = telebot.TeleBot('')
RAPIDAPI_KEY = ""

locations_url = "https://hotels4.p.rapidapi.com/locations/v3/search"

properties_url = "https://hotels4.p.rapidapi.com/properties/v2/list"

location_detail_url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}