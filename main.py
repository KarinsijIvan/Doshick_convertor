import config
import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from pycbrf.toolbox import ExchangeRates

bot = telebot.TeleBot(config.token)

# region links
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
# endregion

ind = 0
output_matrix = []

@bot.message_handler(commands=["start"])
def start(message):
    global ind, output_matrix
    ind, output_matrix = 0, []
    markup = telebot.types.InlineKeyboardMarkup()

    # region create_button
    RUB = telebot.types.InlineKeyboardButton("RUB🇷🇺", callback_data="RUB")
    BYN = telebot.types.InlineKeyboardButton("BYN🇧🇾", callback_data="BYN")
    USD = telebot.types.InlineKeyboardButton("USD🇺🇸", callback_data="USD")
    EUR = telebot.types.InlineKeyboardButton("EUR🇪🇺", callback_data="EUR")
    KZT = telebot.types.InlineKeyboardButton("KZT🇰🇿", callback_data="KZT")
    CNY = telebot.types.InlineKeyboardButton("CNY🇨🇳", callback_data="CNY")
    UAH = telebot.types.InlineKeyboardButton("UAH🇺🇦", callback_data="UAH")
    JPY = telebot.types.InlineKeyboardButton("JPY🇯🇵", callback_data="JPY")
    # endregion

    markup.add(RUB, BYN, USD)
    markup.add(EUR, KZT, CNY)
    markup.add(UAH, JPY)

    bot.send_message(message.chat.id, "Какую валюту вы хотите конвертировать в дошираки?\n"
                                      "Выберете одну из доступных", reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    global ind
    if call.message:
        if call.data == "next":
            ind += 1
            send_doshick_info(call.message)
        elif call.data == "back":
            ind -= 1
            send_doshick_info(call.message)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Сколько у вас {call.data}?")
            bot.register_next_step_handler(call.message, covert_miney_to_doshick, call.data)


def covert_miney_to_doshick(message, currency):
    date = datetime.now().date()
    money = float(message.text)
    rates = ExchangeRates(date)
    sells_and_quantity = {}
    estimations = {}
    output = []

    for i in link_list:
        sell, estimation = get_data(i[0])
        estimations.update({i[1]: estimation})

        if currency != "RUB":
            quantity_doshick = int(float(rates[currency].rate) * money / sell)
            difference = float(rates[currency].rate)
            change = round(money - quantity_doshick * (sell/difference), ndigits=2)
            output.append(f"{quantity_doshick} {i[1]} за {round(sell/difference, ndigits=2)} {currency}\n"
                          f"    Обойдётся в {round(quantity_doshick*(sell/difference), ndigits=2)} {currency}\n"
                          f"    Оценка: {estimation} звёзд\n"
                          f"    Cдача: {round(change, ndigits=2)} {currency}")
        else:
            quantity_doshick = int(money / sell)
            change = round(money - quantity_doshick * sell, ndigits=2)
            output.append(f"{quantity_doshick} {i[1]} за {sell} RUB\n"
                          f"    Обойдётся в {round(quantity_doshick*sell, ndigits=2)} RUB\n"
                          f"    Оценка: {estimation} звёзд\n"
                          f"    Cдача: {round(change, ndigits=2)} RUB")

        sells_and_quantity.update({i[1]: [quantity_doshick, sell]})
        benefit = max_benefit(sells_and_quantity)
        max_estimations = max_estimation(estimations)

    send_message(message, output, benefit, max_estimations, money, currency)


def send_message(message, output, benefit, max_estimations, money, currency):
    global output_matrix, ind
    str_output_matrix = []

    for i in range(len(output)):
        str_output_matrix.append(output[i])
        if (i + 1) % 3 == 0:
            output_matrix.append(str_output_matrix)
            str_output_matrix = []

    if len(output_matrix) * len(output_matrix[0]) != len(output):
        end_str = output[len(output_matrix) * len(output_matrix[0]):]

        if end_str:
            output_matrix.append(end_str)

    bot.send_message(message.chat.id, f"За {money} {currency} выгоднее всего купить {benefit[0]}, т.к. Вы получите {benefit[1]}г")
    bot.send_message(message.chat.id, f"Самая высокая оценка, а именно {max_estimations[1]} у:"
                                      f"\n{', '.join(max_estimations[0])}")

    bot.send_message(message.chat.id, f"за {money} {currency} можно купить")
    send_doshick_info(message)


def send_doshick_info(message):
    global output_matrix, ind
    markup = telebot.types.InlineKeyboardMarkup()

    if ind == 0:
        next = telebot.types.InlineKeyboardButton("➡", callback_data="next")
        markup.add(next)
    elif ind == len(output_matrix)-1:
        back = telebot.types.InlineKeyboardButton("⬅", callback_data="back")
        markup.add(back)
    else:
        next = telebot.types.InlineKeyboardButton("➡", callback_data="next")
        back = telebot.types.InlineKeyboardButton("⬅", callback_data="back")
        markup.add(back, next)

    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, "\n\n".join(output_matrix[ind]), reply_markup=markup)


def get_data(link):
    headers = {"User-Agent": UserAgent().random}

    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, "html.parser")

    sell = soup.findAll("div", {"class": "aJThHsRzJ hsLgGFlow bJThHsRzJ tJThHsRzJ BJThHsRzJ"})
    sell = sell[0].text

    estimation = soup.findAll("div", {"class": "aJThHsRzJ bSbeMcXxl bJThHsRzJ tJThHsRzJ"})
    estimation = estimation[0].text

    return to_float(sell), to_float(estimation)


def to_float(n):
    n = n.split()[0]
    n = n.split(",")
    n = float(".".join(n))

    return n


def max_benefit(lst):
    all_quantity = {}
    for i in lst:
        weight = int(i.split()[-1].rstrip("г"))
        quantity = weight * lst[i][0]
        all_quantity.update({quantity: i})

    max_quantity = [all_quantity[max(list(all_quantity))], max(list(all_quantity))]

    return max_quantity


def max_estimation(estimations):
    res = []
    max_value = max(list(estimations.values()))
    for i in estimations:
        if estimations[i] == max_value:
            res.append(i)

    return res, max_value


bot.polling(none_stop=True)
