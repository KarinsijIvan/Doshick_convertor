import config
import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
from pycbrf.toolbox import ExchangeRates

bot = telebot.TeleBot(config.token)

# region links lapsa
red_doshick_70g = ["https://yarcheplus.ru/product/lapsha-4416", "красный дошик 70г"]
red_doshick_90g = ["https://yarcheplus.ru/product/lapsha-5324", "красный дошик 90г"]

green_doshick_70g = ["https://yarcheplus.ru/product/lapsha-4033", "зелёный дошик 70г"]
green_doshick_90g = ["https://yarcheplus.ru/product/lapsha-4116", "зелёный дошик 90г"]

chicken_rollton_60g = ["https://yarcheplus.ru/product/vermishel-4174", "куриный роллтон 60г"]
chicken_rollton_85g = ["https://yarcheplus.ru/product/lapsha-6707", "куриный роллтон 85г"]
chicken_rollton_90g = ["https://yarcheplus.ru/product/lapsha-4404", "куриный роллтон 90г"]

beef_rollton_60g = ["https://yarcheplus.ru/product/vermishel-3581", "говяжий роллтон 60г"]
beef_rollton_85g = ["https://yarcheplus.ru/product/vermishel-6734", "говяжий роллтон 85г"]
beef_rollton_90g = ["https://yarcheplus.ru/product/lapsha-3940", "говяжий роллтон 90г"]

mushroom_rollton_60g = ["https://yarcheplus.ru/product/vermishel-3779", "грибной роллтон 60г"]

bacon_and_cheese_rollton_60g = ["https://yarcheplus.ru/product/vermishel-5300", "роллтон с беконом и сыром 60г"]
# endregion

# region links sausages
indilait_440g = ["https://yarcheplus.ru/product/sosiski-30725", "«ИНДИлайт» 440г"]

damkov_sliv_300g = ["https://yarcheplus.ru/product/sosiski-8268", "«Дымов» сливочные 300г"]
damkov_milk_300g = ["https://yarcheplus.ru/product/sosiski-6956", "«Дымов» молочные 300г"]

sibargo_sibir_400g = ["https://yarcheplus.ru/product/sosiski-28633", "«Сибагро» мясные по-сибирски 400г"]
sibargo_sliv_300g = ["https://yarcheplus.ru/product/sosiski-34449", "«Сибагро» молочные 300"]
sibargo_milk_420g = ["https://yarcheplus.ru/product/sosiski-18394", "«Сибагро» молочные 420г"]

masniski_rad_420g = ["https://yarcheplus.ru/product/sosiski-17858", "«Мясницкий ряд» 420г"]

gordost_fermera_90g = ["https://yarcheplus.ru/product/sosiski-2932", "«Гордость фермера» 90г"]

masnaa_koleksia_cheese_300g = ["https://yarcheplus.ru/product/sosiski-2641", "«Мясная коллекция» с сыром 300г"]
masnaa_koleksia_slivki_360g = ["https://yarcheplus.ru/product/sosiski-2817", "«Мясная коллекция» со сливками 360г"]
masnaa_koleksia_zavtrak_300g = ["https://yarcheplus.ru/product/sosiski-31179", "«Мясная коллекция» на завтрак 300г"]
masnaa_koleksia_derevna_620g = ["https://yarcheplus.ru/product/sosiski-35438", "«Мясная коллекция» Деревенские 620г"]

bavarskie_350g = ["https://yarcheplus.ru/product/sosiski-18258", "«Торговая площадь» Баварские 350г"]

spk_360g = ["https://yarcheplus.ru/product/sosiski-2600", "«СПК» молочные 360г"]

big_sos_340g = ["https://yarcheplus.ru/product/sosiski-2714", "«BigSos» Большая SOSиска 340г"]

vazonka_330g = ["https://yarcheplus.ru/product/sosiski-35548", "«Вязанка» Сливушки 330г"]
# endregion

ind = 0
output_matrix = []
estimations = {}
sells_and_quantity = {}

link_list = []

@bot.message_handler(commands=["start"])
def start(message):
    global ind, output_matrix, link_list, estimations, sells_and_quantity
    ind, output_matrix, link_list, estimations, sells_and_quantity = 0, [], [], {}, {}

    markup = telebot.types.InlineKeyboardMarkup()

    sausages = telebot.types.InlineKeyboardButton("сосиски", callback_data="sausages")
    laspa = telebot.types.InlineKeyboardButton("Лапша бп", callback_data="laspa")

    markup.add(sausages, laspa)

    bot.send_message(message.chat.id, "выберите категорию товара", reply_markup=markup)


def get_currency(message):
    global ind, output_matrix

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

    bot.send_message(message.chat.id, "Какую валюту вы хотите конвертировать в товар?\n"
                                      "Выберете одну из доступных", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global ind, link_list
    if call.message:

        if call.data == "laspa":
            link_list = [red_doshick_70g, red_doshick_90g,
                         green_doshick_70g, green_doshick_90g,
                         chicken_rollton_60g, chicken_rollton_85g, chicken_rollton_90g,
                         beef_rollton_60g, beef_rollton_85g, beef_rollton_90g,
                         mushroom_rollton_60g,
                         bacon_and_cheese_rollton_60g]
            get_currency(call.message)

        elif call.data == "sausages":
            link_list = [indilait_440g, damkov_sliv_300g, damkov_milk_300g,
                         sibargo_sibir_400g, sibargo_sliv_300g, sibargo_milk_420g,
                         masniski_rad_420g, gordost_fermera_90g, masnaa_koleksia_cheese_300g,
                         masnaa_koleksia_slivki_360g, masnaa_koleksia_zavtrak_300g, masnaa_koleksia_derevna_620g,
                         bavarskie_350g, spk_360g, big_sos_340g, vazonka_330g]
            get_currency(call.message)

        elif call.data == "next":
            ind += 1
            send_doshick_info(call.message)
        elif call.data == "back":
            ind -= 1
            send_doshick_info(call.message)

        elif call.data == "info":
            send_estimations_info(call.message)

        else:
            bot.send_message(call.message.chat.id, f"Сколько у вас {call.data}?")
            bot.register_next_step_handler(call.message, covert_miney_to_lapsa, call.data)


def covert_miney_to_lapsa(message, currency):
    global estimations, sells_and_quantity, link_list
    date = datetime.now().date()

    try:
        money = float(message.text)

        rates = ExchangeRates(date)
        output = []

        for i in link_list:
            sell, estimation = get_data(i[0])
            estimations.update({i[1]: estimation})

            if currency != "RUB":
                if sell == 0.0:
                    output.append(f"{i[1]} Нет в наличии\n"
                                  f"    Оценка: {estimation} звёзд")
                else:
                    quantity = int(float(rates[currency].rate) * money / sell)
                    difference = float(rates[currency].rate)
                    change = round(money - quantity * (sell/difference), ndigits=2)
                    output.append(f"{quantity} {i[1]} за {round(sell/difference, ndigits=2)} {currency}\n"
                                  f"    Обойдётся в {round(quantity*(sell/difference), ndigits=2)} {currency}\n"
                                  f"    Оценка: {estimation} звёзд\n"
                                  f"    Cдача: {round(change, ndigits=2)} {currency}")
            else:
                if sell == 0.0:
                    output.append(f"{i[1]} Нет в наличии\n"
                                  f"    Оценка: {estimation} звёзд")
                else:
                    quantity = int(money / sell)
                    change = round(money - quantity * sell, ndigits=2)
                    output.append(f"{quantity} {i[1]} за {sell} RUB\n"
                                  f"    Обойдётся в {round(quantity*sell, ndigits=2)} RUB\n"
                                  f"    Оценка: {estimation} звёзд\n"
                                  f"    Cдача: {round(change, ndigits=2)} RUB")

            sells_and_quantity.update({i[1]: [quantity, sell]})
            benefit = max_benefit(sells_and_quantity)
            max_estimations = max_estimation(estimations)

        send_message(message, output, benefit, max_estimations, money, currency)

    except ValueError:
        bot.send_message(message.chat.id, "Данные введены не коректно, напишите /start для повторной попытки")

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

    markup = telebot.types.InlineKeyboardMarkup()
    info = telebot.types.InlineKeyboardButton("Подробнее про оценки", callback_data="info")
    markup.add(info)

    bot.send_message(message.chat.id, f"За {money} {currency} выгоднее всего купить {', '.join(benefit[0])}, т.к. Вы получите {benefit[1]}г")
    bot.send_message(message.chat.id, f"Самая высокая оценка, а именно {max_estimations[1]} у:"
                                      f"\n{', '.join(max_estimations[0])}", reply_markup=markup)

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


def send_estimations_info(message):
    bot.send_message(message.chat.id, "Функция временно не доступна")
    # global sells_and_quantity
    # estimations_5_45 = {}
    # estimations_44_4 = {}
    # estimations_39_3 = {}
    # estimations_29_0 = {}
    # for i in sells_and_quantity:
    #     if estimations[i] > 4.4:
    #         estimations_5_45.update({i: sells_and_quantity[i]})
    #     elif 3.9 < estimations[i] < 4.5:
    #         estimations_44_4.update({i: sells_and_quantity[i]})
    #     elif 2.9 < estimations[i] < 4:
    #         estimations_39_3.update({i: sells_and_quantity[i]})
    #     elif estimations[i] < 3:
    #         estimations_29_0.update({i: sells_and_quantity[i]})
    # if estimations_5_45:
    #     res = []
    #     for i in estimations_5_45:
    #
    #     # send_message(message.chat.id, "⭐5 - 4.5⭐\n"
    #     #                               "")
    # print(estimations_5_45)
    # print(max_benefit(estimations_5_45))
    # print(estimations_44_4)
    # print(max_benefit(estimations_44_4))


def get_data(link):
    headers = {"User-Agent": UserAgent().random}

    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, "html.parser")

    sell = soup.findAll("div", {"class": "aJThHsRzJ hsLgGFlow bJThHsRzJ tJThHsRzJ BJThHsRzJ"})
    sell = sell[0].text

    try:
        estimation = soup.findAll("div", {"class": "aJThHsRzJ bSbeMcXxl bJThHsRzJ tJThHsRzJ"})
        estimation = estimation[0].text
    except:
        estimation = "0,0"

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

        if not(quantity in list(all_quantity.keys())):
            all_quantity.update({quantity: [i]})
        else:
            all_quantity[quantity].append(i)

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
