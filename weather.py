import requests
import datetime
from config import open_weather_token, code_to_weather

def getweather():
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q=Yekaterinburg&appid={open_weather_token}&units=metric")
        data = r.json()

        weather_description = data["weather"][0]["main"]
        #print (weather_description)
        if weather_description in code_to_weather:
            wd = code_to_weather[weather_description]
        else:
            wd = ["Не дописал"]

        weather_day = data["main"]["temp_max"]
        weather_night = data["main"]["temp_min"]
        humidity = data["main"]["humidity"]
        pressure = (data["main"]["pressure"]/1,333)
        weather_today = (f"***{datetime.datetime.now().strftime(('%d-%m-%Y %H:%M'))}***\n"
                             f"Сегодня в Екатеринбурге будет {wd}\nТемпература днем: {round(weather_day)}C°\n"
                             f"Влажность: {humidity}%\nДавление: {round(pressure)}мм.рт.ст.\n"

                             f"Хорошего дня")
        return weather_today
    except ():
        pass
