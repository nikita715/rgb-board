import time
from dataclasses import dataclass

import requests

URL = "http://api.openweathermap.org/data/2.5/weather"


@dataclass
class WeatherData:
    temp: str
    temp_feels: str
    icon: str


class Weather:
    def __init__(self, api_key, city, refresh_seconds):
        self.params = {"q": city, "appid": api_key, "units": "metric"}
        self.refresh_seconds = refresh_seconds
        self.data = None
        self.fetched_at = 0

    def get(self):
        if self.data is None or time.monotonic() - self.fetched_at > self.refresh_seconds:
            try:
                self.data = self.fetch()
                self.fetched_at = time.monotonic()
            except Exception as e:
                print(f"[weather] fetch failed: {e}")
        return self.data

    def fetch(self):
        response = requests.get(URL, params=self.params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return WeatherData(
            temp=f"{int(data['main']['temp'])}°",
            temp_feels=f"{int(data['main']['feels_like'])}°",
            icon=icon_for(str(data["weather"][0]["id"])),
        )


def icon_for(code):
    # https://openweathermap.org/weather-conditions
    match code[0]:
        case "2":
            return "⛈︎"
        case "3" | "5":
            return "🌧︎"
        case "6":
            return "🌨︎"
        case "7":
            return "☁︎"
        case "8":
            match code[2]:
                case "0":
                    return "☀︎"
                case "1":
                    return "⛅"
                case _:
                    return "☁︎"
        case _:
            return ""
