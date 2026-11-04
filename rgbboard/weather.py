import threading
import time
from dataclasses import dataclass

import requests

URL = "http://api.openweathermap.org/data/2.5/weather"
RETRY_SECONDS = 60

EMOJI = {
    "clear": "☀︎",
    "partly": "⛅",
    "cloudy": "☁︎",
    "fog": "☁︎",
    "rain": "🌧︎",
    "snow": "🌨︎",
    "storm": "⛈︎",
}


@dataclass(frozen=True)
class WeatherData:
    temp: str
    temp_feels: str
    kind: str  # a key of EMOJI, or "" if unknown

    @property
    def icon(self):
        return EMOJI.get(self.kind, "")


class Weather:
    """Cached weather. get() never blocks: a stale cache is refreshed in a background thread,
    so animations keep running while the API is slow."""

    def __init__(self, api_key, city, refresh_seconds):
        self.params = {"q": city, "appid": api_key, "units": "metric"}
        self.refresh_seconds = refresh_seconds
        self.data = None
        self.next_fetch = 0
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            if time.monotonic() >= self.next_fetch:
                self.next_fetch = float("inf")  # one fetch at a time
                threading.Thread(target=self.refresh, daemon=True).start()
        return self.data

    def refresh(self):
        delay = RETRY_SECONDS
        try:
            self.data = self.fetch()
            delay = self.refresh_seconds
        except Exception as e:
            print(f"[weather] fetch failed: {e}")
        with self.lock:
            self.next_fetch = time.monotonic() + delay

    def fetch(self):
        response = requests.get(URL, params=self.params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return WeatherData(
            temp=f"{round(data['main']['temp'])}°",
            temp_feels=f"{round(data['main']['feels_like'])}°",
            kind=kind_for(data["weather"][0]["id"]),
        )


def kind_for(code):
    # https://openweathermap.org/weather-conditions
    match code // 100:
        case 2:
            return "storm"
        case 3 | 5:
            return "rain"
        case 6:
            return "snow"
        case 7:
            return "fog"
        case 8:
            return {800: "clear", 801: "partly", 802: "partly"}.get(code, "cloudy")
        case _:
            return ""
