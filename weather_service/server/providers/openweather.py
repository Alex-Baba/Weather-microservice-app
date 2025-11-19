import os
from typing import Dict, Optional

import requests

from .base import WeatherProvider, ProviderError, CityNotFoundError
from weather_service.server.config import settings


class OpenWeatherProvider(WeatherProvider):
    API_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise RuntimeError("OpenWeather API key not configured")

    def fetch_weather(self, city: str) -> Dict[str, object]:
        try:
            resp = requests.get(
                self.API_URL,
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status == 404:
                raise CityNotFoundError(f"city not found: {city}") from e
            raise ProviderError(f"http error {status}") from e
        except requests.RequestException as e:
            raise ProviderError("network error") from e

        try:
            main = data.get("main", {}) or {}
            weather = (data.get("weather") or [{}])[0] or {}
            wind = data.get("wind", {}) or {}

            return {
                "city_name": data.get("name", city),
                "temperature": float(main.get("temp", 0.0)),
                "humidity": int(main.get("humidity", 0)),
                "description": str(weather.get("description", "")),
                "wind_speed": float(wind.get("speed", 0.0)),
            }
        except Exception as e:
            raise ProviderError("failed to parse provider response") from e
