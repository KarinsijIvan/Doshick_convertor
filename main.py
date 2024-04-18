import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from pycbrf.toolbox import ExchangeRates

bot = telebot.TeleBot("Не спалю))")

red_doshick_70g = "https://yarcheplus.ru/product/lapsha-4416"
red_doshick_90g = "https://yarcheplus.ru/product/lapsha-5324"

green_doshick_70g = "https://yarcheplus.ru/product/lapsha-4033"
green_doshick_90g = "https://yarcheplus.ru/product/lapsha-4116"

chicken_rolton_60g = "https://yarcheplus.ru/product/vermishel-4174"

chicken_rolton_85g = "https://yarcheplus.ru/product/lapsha-6707"
chicken_rolton_90g = "https://yarcheplus.ru/product/lapsha-4404"

beef_rolton_60g = "https://yarcheplus.ru/product/vermishel-3581"
beef_rolton_85g = "https://yarcheplus.ru/product/vermishel-6734"
beef_rolton90g = "https://yarcheplus.ru/product/lapsha-3940"

mushroom_rolton_60g = "https://yarcheplus.ru/product/vermishel-3779"

bacon_and_cheese_rolton_60g = "https://yarcheplus.ru/product/vermishel-5300"

@bot.message_handler(commands=["convert"])
def convert(message):
    bot.send_message(message.chat.id, "Какую валюту вы хотите конвертировать в дошираки?\n"
                                      "Выберете одну из доступных")

    bot.send_message(message.chat.id, "Доступные валюты:\n"
                                      "RUB🇷🇺\n"
                                      "BYN🇧🇾\n"
                                      "USD🇺🇸\n"
                                      "EUR🇪🇺\n"
                                      "KZT🇰🇿\n"
                                      "CNY🇨🇳\n"
                                      "UAH🇺🇦\n"
                                      "JPY🇯🇵")


def covert_miney_to_doshick(currency, money, sell):
    date = datetime.now.date()
    rates = ExchangeRates(date)
    return int(rates[currency].rate * money / sell)

def get_sell(link):
    headers = {"User-Agent": UserAgent().random}

    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, "html.parser")

    sell = soup.findAll("div", {"class": "aJThHsRzJ hsLgGFlow bJThHsRz UThHsRzJ BJThHsRzJ"})
    sell = sell[0].text

    return sell_to_float(sell)

def sell_to_float(sell):
    sell = sell.split()[0]
    sell = sell.split(",")
    sell = float(".".join(sell))

    return sell

bot.polling(none_stop=True)
# RUB🇷🇺\n
# BYN🇧🇾\n
# USD🇺🇸\n
# EUR🇪🇺\n
# KZT🇰🇿\n
# CNY🇨🇳\n
# UAH🇺🇦\r
# JPY🇯🇵")