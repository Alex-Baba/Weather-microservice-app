import types
import requests
import pytest

from weather_service.server.providers.openweather import OpenWeatherProvider
from weather_service.server.providers.base import CityNotFoundError, ProviderError


class DummyResponse:
    def __init__(self, json_data, status=200):
        self._json = json_data
        self.status = status
        self.status_code = status

    def raise_for_status(self):
        if self.status >= 400:
            err = requests.HTTPError(f"{self.status} Client Error")
            err.response = types.SimpleNamespace(status_code=self.status)
            raise err

    def json(self):
        return self._json


SAMPLE = {
    "name": "TestCity",
    "main": {"temp": 15.2, "humidity": 55},
    "weather": [{"description": "patchy clouds"}],
    "wind": {"speed": 1.8},
}


def test_fetch_weather_success(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummykey")

    def fake_get(url, params=None, timeout=None):
        assert "weather" in url
        assert params.get("q") == "TestCity"
        return DummyResponse(SAMPLE, status=200)

    monkeypatch.setattr("requests.get", fake_get)

    provider = OpenWeatherProvider()
    data = provider.fetch_weather("TestCity")

    assert data["city_name"] == "TestCity"
    assert abs(data["temperature"] - 15.2) < 0.001
    assert data["humidity"] == 55
    assert data["description"] == "patchy clouds"
    assert abs(data["wind_speed"] - 1.8) < 0.001


def test_fetch_weather_not_found(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummykey")

    def fake_get_404(url, params=None, timeout=None):
        return DummyResponse({"cod": "404", "message": "city not found"}, status=404)

    monkeypatch.setattr("requests.get", fake_get_404)

    provider = OpenWeatherProvider()
    with pytest.raises(CityNotFoundError):
        provider.fetch_weather("NoSuchCity")


def test_fetch_weather_network_error(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummykey")

    def fake_get_err(url, params=None, timeout=None):
        raise requests.RequestException("network down")

    monkeypatch.setattr("requests.get", fake_get_err)

    provider = OpenWeatherProvider()
    with pytest.raises(ProviderError):
        provider.fetch_weather("TestCity")
