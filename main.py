import telebot
from telebot import types
from city import *

bot = telebot.TeleBot(get_token())


@bot.message_handler(commands=['start'])
def send_welcome(message):
    message_text = ('Приветствую, это AstroBot, созданный учениками Лицея.\n\n'
                    'Прежде чем начать, нужно ввести свой город:')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button3 = types.KeyboardButton('Не сообщу')

    markup.add(button3)

    bot.send_message(message.chat.id, message_text, reply_markup=markup)


button_state = {
    'facts': False,  # False - крестик, True - галочка
    'inspiration': False,
    'iss_visibility': False
}


@bot.message_handler(commands=['today'])
def sun(message):
    res = get_apod()
    bot.reply_to(message, res)


@bot.message_handler(commands=['solar'])
def sun(message):
    res = get_solar_activity()
    bot.reply_to(message, res)


@bot.message_handler(commands=['vdox'])
def vdox(message):
    res = get_quote(message.chat.id)
    bot.reply_to(message, res)


@bot.message_handler(commands=['general'])
def send_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_facts = types.KeyboardButton(f"Факты о космосе {'✔️' if button_state['facts'] else '❌'}")
    btn_inspiration = types.KeyboardButton(f"Вдохновение {'✔️' if button_state['inspiration'] else '❌'}")
    btn_iss_visibility = types.KeyboardButton(f"Видимость МКС {'✔️' if button_state['iss_visibility'] else '❌'}")

    markup.add(btn_facts, btn_inspiration, btn_iss_visibility)

    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


@bot.message_handler(commands=['moon'])
def moon_phase(message):
    phase = get_moon_phase()
    bot.reply_to(message, f"Текущая фаза Луны: {phase}")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text.startswith('Факты о космосе'):
        # Переключаем состояние кнопки
        button_state['facts'] = not button_state['facts']
        update_buttons(message)

    elif message.text.startswith('Вдохновение'):
        button_state['inspiration'] = not button_state['inspiration']
        update_buttons(message)

    elif message.text.startswith('Видимость МКС'):
        button_state['iss_visibility'] = not button_state['iss_visibility']
        update_buttons(message)
    elif message.text == 'Настройки':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Ввод города')
        markup.add(button1)
        bot.reply_to(message, 'Настройки\n'
                              '', reply_markup=markup)
    elif message.text == 'Ввод города':
        pass
    elif message.text == 'Автоматическая отправка':
        bot.reply_to(message, 'Вы выбрали кнопку 2')
    elif message.text == 'Не сообщу':
        write_city(message.chat.id, 'Москва')
        bot.reply_to(message, 'Хорошо, поставили для вас Москву', reply_markup=None)
    else:
        ans = is_exist(message.text)
        if ans:
            write_city(message.chat.id, message.text)
            bot.reply_to(message, f'Ваш город: {message.text}, {translate_text(ans[4], dest_lang="ru")}. Записали.')
        else:
            bot.reply_to(message, 'Город не найден. Попробуй ввести более крупный ближайший город.')


def update_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_facts = types.KeyboardButton(f"Факты о космосе {'✔️' if button_state['facts'] else '❌'}")
    btn_inspiration = types.KeyboardButton(f"Вдохновение {'✔️' if button_state['inspiration'] else '❌'}")
    btn_iss_visibility = types.KeyboardButton(f"Видимость МКС {'✔️' if button_state['iss_visibility'] else '❌'}")

    markup.add(btn_facts, btn_inspiration, btn_iss_visibility)

    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_city(message):
    city = message.text.strip()
    coords = get_coordinates(city)
    if not coords:
        bot.send_message(message.chat.id, "Не удалось определить координаты указанного региона.")
        return

    lat, lon = coords
    stars = get_visible_stars(lat, lon)

    if stars:
        response = f"Топ {len(stars)} ярких звёзд, видимых в {city.title()}:\n"
        for name, mag, alt in stars:
            response += f"- {name}: зв. величина {mag:.2f}, высота {alt:.1f} градусов.\n"
    else:
        response = "Сейчас ни одна яркая звезда не видна."

    bot.send_message(message.chat.id, response)

bot.infinity_polling()
