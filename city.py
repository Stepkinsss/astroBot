import random
import requests
from googletrans import Translator
import pandas as pd
import datetime
import ephem
from datetime import datetime
from skyfield.data import hipparcos
from skyfield.api import load, Topos, Star
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

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

hip_to_name = {
    32349: "Сириус", 71683: "Альфа-Центавра", 91262: "Вега", 113368: "Фомальгаут",
    24608: "Процион", 37279: "Бетельгейзе", 24436: "Капелла", 53910: "Поллукс",
    87833: "Денеб", 69673: "Арктур", 11767: "Альдебаран", 97649: "Альтаир",
    21421: "Беллатрикс", 7588: "Ахернар", 677: "Хамаль", 65474: "Регула",
    17651: "Ригель", 82273: "Спика", 59774: "Кастор",
}

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="astro_star_viewer")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None
#местное время для точности определения звёзд
def get_local_time(lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if tz_name:
        local_tz = pytz.timezone(tz_name)
        return datetime.now(local_tz)
    else:
        return None

def get_visible_stars(lat, lon, max_objects=5):
    local_time = get_local_time(lat, lon)
    if not local_time:
        return []
    t = ts.from_datetime(local_time)
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

    visible = []
    for hip_id, star in stars_df.iterrows():
        ra_hours = star['ra_degrees'] / 15.0
        dec_deg = star['dec_degrees']
        mag = star['magnitude']
        sky_star = Star(ra_hours=ra_hours, dec_degrees=dec_deg)
        alt, az, _ = observer.at(t).observe(sky_star).apparent().altaz()
        if alt.degrees > 0:
            name = hip_to_name.get(hip_id, f"HIP {hip_id}")
            visible.append((name, mag, alt.degrees))
    visible.sort(key=lambda x: (x[1], -x[2]))
    return visible[:max_objects]
    
