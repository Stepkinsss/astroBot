import random

import requests
from googletrans import Translator
import pandas as pd
import datetime
import ephem

df = pd.read_csv('worldcities.csv')


def translate_text(text, src_lang='auto', dest_lang='en'):
    translator = Translator()
    translated = translator.translate(text, src=src_lang, dest=dest_lang)

    return translated.text


def is_exist(city):
    city = translate_text(city)
    if not df[df['city'] == city].empty:
        return df[df['city'] == city].to_numpy().tolist()[0]
    else:
        return False


def write_city(user_id, city):
    df_info = pd.DataFrame(pd.read_csv('info.csv'))
    df_info.loc[len(df)] = {'id': user_id, 'city': city, 'time_join': datetime.datetime.now()}
    df_info.to_csv('info.csv', index=False)


def get_moon_phase():
    # Получаем текущую дату
    current_date = ephem.now()

    # Определяем фазу Луны
    phase = ephem.Moon(current_date).phase

    if phase < 1:
        return "Новолуние"
    elif phase < 50:
        return "Растущий месяц"
    elif phase < 51:
        return "Полнолуние"
    else:
        return "Убывающая луна"


def get_quote(id, file_path="quotes.txt"):
    with open(file_path, encoding='utf-8') as file:
        quotes = [line.strip() for line in file if line.strip()]
    df_info = pd.DataFrame(pd.read_csv('info.csv'))
    join_date_str = df_info[df_info['id'] == id].to_numpy().tolist()[0][-1]
    print(join_date_str)
    join_date = datetime.datetime.strptime(join_date_str, "%Y-%m-%d %H:%M:%S.%f")
    days_since_join = (datetime.datetime.now() - join_date).days
    random.seed(id)
    random.shuffle(quotes)
    quote_index = days_since_join % len(quotes)
    return quotes[quote_index]


def get_solar_activity():
    url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            current_k_index = data[-1]['kp_index']
            return f"Текущий индекс солнечной активности (K-индекс): {current_k_index}"
        else:
            return "Не удалось получить данные о солнечной активности."
    else:
        return "Произошла ошибка при получении данных о солнечной активности."


def get_apod():
    url = "https://api.nasa.gov/planetary/apod?api_key=kcx7gYJkHn35oxN7w3VEbk4Jyja0DPb7hWAMpVQw"
    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()
        title = data['title']
        explanation = data['explanation']
        image_url = data['url']

        title = translate_text(title, dest_lang='ru')
        explanation = translate_text(explanation, dest_lang='ru')

        return f"{title}\n\n{explanation}\n{image_url}"
    else:
        return "Не удалось получить данные."


def get_token():
    with open('token.txt', encoding='utf-8') as f:
        lines = [line.strip() for line in f]
    return lines[0]
