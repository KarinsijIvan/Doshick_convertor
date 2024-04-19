import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from pycbrf.toolbox import ExchangeRates

bot = telebot.TeleBot("здесь могла быть выша реклама")

red_doshick_70g = "https://yarcheplus.ru/product/lapsha-4416"
red_doshick_90g = "https://yarcheplus.ru/product/lapsha-5324"

green_doshick_70g = "https://yarcheplus.ru/product/lapsha-4033"
green_doshick_90g = "https://yarcheplus.ru/product/lapsha-4116"

chicken_rolton_60g = "https://yarcheplus.ru/product/vermishel-4174"
chicken_rolton_85g = "https://yarcheplus.ru/product/lapsha-6707"
chicken_rolton_90g = "https://yarcheplus.ru/product/lapsha-4404"

beef_rolton_60g = "https://yarcheplus.ru/product/vermishel-3581"
beef_rolton_85g = "https://yarcheplus.ru/product/vermishel-6734"
beef_rolton_90g = "https://yarcheplus.ru/product/lapsha-3940"

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

    bot.send_message(message.chat.id, "Напишите сообщение  формате: \"сумма валюта\"")

    bot.register_next_step_handler(message, covert_miney_to_doshick)


def covert_miney_to_doshick(message):
    date = datetime.now().date()
    money, currency = message.text.split()
    money = float(money)
    sell = get_sell(red_doshick_70g)
    rates = ExchangeRates(date)

    if currency != "RUB":
        quantity_doshick = int(float(rates[currency].rate) * money / sell)
    else:
        quantity_doshick = int(money / sell)

    bot.send_message(message.chat.id, f"за {message.text} можно купить {quantity_doshick} доширака")
    return quantity_doshick


def get_sell(link):
    headers = {"User-Agent": UserAgent().random}

    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, "html.parser")

    sell = soup.findAll("div", {"class": "aJThHsRzJ hsLgGFlow bJThHsRzJ tJThHsRzJ BJThHsRzJ"})
    sell = sell[0].text

    return sell_to_float(sell)


def sell_to_float(sell):
    sell = sell.split()[0]
    sell = sell.split(",")
    sell = float(".".join(sell))

    return sell


bot.polling(none_stop=True)
