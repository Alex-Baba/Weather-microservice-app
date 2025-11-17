from abc import ABC, abstractmethod
from typing import Dict


class ProviderError(Exception):
    """Generic provider error (network, 5xx, parse)."""


class CityNotFoundError(ProviderError):
    """Raised when the provider returns 404 / unknown city."""


class WeatherProvider(ABC):
    @abstractmethod
    def fetch_weather(self, city: str) -> Dict[str, object]:
        """
        Fetch and return normalized weather dict:
        {
          "city_name": str,
          "temperature": float,
          "humidity": int,
          "description": str,
          "wind_speed": float
        }
        Raise CityNotFoundError for 404, ProviderError for other failures.
        """
        raise NotImplementedError