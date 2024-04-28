import config
import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from pycbrf.toolbox import ExchangeRates

bot = telebot.TeleBot(config.token)

red_doshick_70g = ["https://yarcheplus.ru/product/lapsha-4416", "красный дошик 70г"]
red_doshick_90g = ["https://yarcheplus.ru/product/lapsha-5324", "красный дошик 90г"]

green_doshick_70g = ["https://yarcheplus.ru/product/lapsha-4033", "зелёный дошик 70г"]
green_doshick_90g = ["https://yarcheplus.ru/product/lapsha-4116", "зелёный дошик 90г"]

chicken_rolton_60g = ["https://yarcheplus.ru/product/vermishel-4174", "куриный ролтон 60г"]
chicken_rolton_85g = ["https://yarcheplus.ru/product/lapsha-6707", "куриный ролтон 85г"]
chicken_rolton_90g = ["https://yarcheplus.ru/product/lapsha-4404", "куриный ролтон 90г"]

beef_rolton_60g = ["https://yarcheplus.ru/product/vermishel-3581", "говяжий ролтон 60г"]
beef_rolton_85g = ["https://yarcheplus.ru/product/vermishel-6734", "говяжий ролтон 85г"]
beef_rolton_90g = ["https://yarcheplus.ru/product/lapsha-3940", "говяжий ролтон 90г"]

mushroom_rolton_60g = ["https://yarcheplus.ru/product/vermishel-3779", "грибной ролтон 60г"]

bacon_and_cheese_rolton_60g = ["https://yarcheplus.ru/product/vermishel-5300", "ролтон с беконом и сыром 60г"]

link_list = [red_doshick_70g, red_doshick_90g,
             green_doshick_70g, green_doshick_90g,
             chicken_rolton_60g, chicken_rolton_85g, chicken_rolton_90g,
             beef_rolton_60g, beef_rolton_85g, beef_rolton_90g,
             mushroom_rolton_60g,
             bacon_and_cheese_rolton_60g]


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
    rates = ExchangeRates(date)
    sells_and_quantity = {}

    bot.send_message(message.chat.id, f"за {message.text} можно купить")
    for i in link_list:
        sell = get_sell(i[0])

        if currency != "RUB":
            quantity_doshick = int(float(rates[currency].rate) * money / sell)
        else:
            quantity_doshick = int(money / sell)

        change = round(money - quantity_doshick*sell, ndigits=2)
        sells_and_quantity.update({i[1]: [quantity_doshick, sell]})

        bot.send_message(message.chat.id, f"{quantity_doshick} {i[1]} за {sell}, {change} останется")

    benefit = max_benefit(sells_and_quantity)
    bot.send_message(message.chat.id, f"Выгоднее всего купить {benefit[0]}, т.к. Вы получите {benefit[1]}г")

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


def max_benefit(lst):
    all_quantity = {}
    for i in lst:
        weight = int(i.split()[-1].rstrip("г"))
        quantity = weight * lst[i][0]
        all_quantity.update({quantity: i})

    max_quantity = [all_quantity[max(list(all_quantity))], max(list(all_quantity))]

    print(max_quantity)
    return max_quantity


bot.polling(none_stop=True)
