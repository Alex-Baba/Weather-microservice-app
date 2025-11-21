import importlib
import types
import requests


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


class DummyContext:
    def __init__(self, metadata=None):
        # metadata should be an iterable of tuples
        self._md = metadata or []

    def invocation_metadata(self):
        return list(self._md)

    def abort(self, code, message):
        raise RuntimeError(f"gRPC abort: {code} {message}")


SAMPLE_SUCCESS = {
    "name": "Barcelona",
    "main": {"temp": 21.5, "humidity": 60},
    "weather": [{"description": "clear sky"}],
    "wind": {"speed": 3.2},
}


def reload_server(monkeypatch):
    """Reload the server module so it re-reads env vars like OPENWEATHER_API_KEY."""
    import weather_service.server.weather_server as srv

    return importlib.reload(srv)


def test_getweather_success(monkeypatch):
    # ensure env key present before importing
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummy")
    monkeypatch.setenv("GRPC_API_KEY", "secret123")
    srv = reload_server(monkeypatch)

    # mock requests.get used inside server
    def fake_get(url, params=None, timeout=None):
        assert url.endswith("/weather")
        return DummyResponse(SAMPLE_SUCCESS, status=200)

    monkeypatch.setattr(srv.requests, "get", fake_get)

    req = srv.weather_pb2.WeatherRequest(city_name="Barcelona")
    ctx = DummyContext(metadata=[("x-api-key", "secret123")])
    resp = srv.WeatherServicer().GetWeather(req, ctx)

    assert resp.city_name == "Barcelona"
    assert abs(resp.temperature - 21.5) < 0.001
    assert resp.humidity == 60
    assert resp.description == "clear sky"
    assert abs(resp.wind_speed - 3.2) < 0.001
    # fetched_at should be set
    assert resp.HasField("fetched_at")


def test_getweather_auth_failure(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummy")
    monkeypatch.setenv("GRPC_API_KEY", "secret123")
    srv = reload_server(monkeypatch)

    req = srv.weather_pb2.WeatherRequest(city_name="London")
    ctx = DummyContext(metadata=[("x-api-key", "wrong-key")])
    try:
        srv.WeatherServicer().GetWeather(req, ctx)
        assert False, "expected abort"
    except RuntimeError as e:
        assert "UNAUTHENTICATED" in str(e)


def test_getweather_missing_api_key(monkeypatch):
    # ensure OPENWEATHER_API_KEY is empty (avoid loading from .env)
    monkeypatch.setenv("OPENWEATHER_API_KEY", "")
    monkeypatch.setenv("GRPC_API_KEY", "secret123")
    srv = reload_server(monkeypatch)

    req = srv.weather_pb2.WeatherRequest(city_name="Paris")
    ctx = DummyContext(metadata=[("x-api-key", "secret123")])
    try:
        srv.WeatherServicer().GetWeather(req, ctx)
        assert False, "expected abort"
    except RuntimeError as e:
        assert "missing OPENWEATHER_API_KEY" in str(e)


def test_getweather_provider_http_error(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummy")
    monkeypatch.setenv("GRPC_API_KEY", "secret123")
    srv = reload_server(monkeypatch)

    def fake_get_404(url, params=None, timeout=None):
        return DummyResponse({"cod": "404", "message": "city not found"}, status=404)

    monkeypatch.setattr(srv.requests, "get", fake_get_404)

    req = srv.weather_pb2.WeatherRequest(city_name="NoSuchCity")
    ctx = DummyContext(metadata=[("x-api-key", "secret123")])
    try:
        srv.WeatherServicer().GetWeather(req, ctx)
        assert False, "expected abort"
    except RuntimeError:
        pass
