import builtins
from unittest import mock


def make_resp(city="TestCity", temp=10.0, humidity=50, desc="clear", wind=1.2, error=""):
    class Resp:
        def __init__(self):
            self.city_name = city
            self.temperature = temp
            self.humidity = humidity
            self.description = desc
            self.wind_speed = wind
            self.error = error

    return Resp()


def test_client_prints_weather(monkeypatch, capsys):
    # mock input
    monkeypatch.setattr(builtins, "input", lambda prompt="": "London")

    # mock the stub and its GetWeather method
    fake_resp = make_resp(city="London", temp=18.6, humidity=82, desc="light rain", wind=4.6)

    class FakeStub:
        def GetWeather(self, req, metadata=None, timeout=None):
            return fake_resp

    fake_module = mock.MagicMock()
    fake_module.WeatherServiceStub.return_value = FakeStub()

    with mock.patch("weather_service.client.client.weather_pb2_grpc", fake_module):
        with mock.patch("weather_service.client.client.weather_pb2") as pb:
            # create a fake request class to satisfy construction (not used)
            pb.WeatherRequest = lambda **kwargs: mock.MagicMock()
            # run main
            from weather_service.client import client

            client.main()

    captured = capsys.readouterr()
    assert "Weather for London:" in captured.out
    assert "Temperature: 18.6" in captured.out
    assert "Humidity: 82%" in captured.out


def test_client_handles_error(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "NoCity")

    fake_resp = make_resp(error="city not found")

    class FakeStub:
        def GetWeather(self, req, metadata=None, timeout=None):
            return fake_resp

    fake_module = mock.MagicMock()
    fake_module.WeatherServiceStub.return_value = FakeStub()

    with mock.patch("weather_service.client.client.weather_pb2_grpc", fake_module):
        with mock.patch("weather_service.client.client.weather_pb2") as pb:
            pb.WeatherRequest = lambda **kwargs: mock.MagicMock()
            from weather_service.client import client
            client.main()

    captured = capsys.readouterr()
    assert "Error: city not found" in captured.out
