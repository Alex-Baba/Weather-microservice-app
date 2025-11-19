from typing import Dict
from generated.proto import weather_pb2


def dict_to_weather_response(data: Dict) -> weather_pb2.WeatherResponse:
    """Convert a normalized weather dict to a protobuf WeatherResponse."""
    return weather_pb2.WeatherResponse(
        city_name=data.get("city_name", ""),
        temperature=float(data.get("temperature", 0.0)),
        humidity=int(data.get("humidity", 0)),
        description=str(data.get("description", "")),
        wind_speed=float(data.get("wind_speed", 0.0)),
        error=str(data.get("error", "")),
    )


def weather_response_to_dict(msg: weather_pb2.WeatherResponse) -> Dict:
    """Convert a protobuf WeatherResponse to a plain dict."""
    return {
        "city_name": msg.city_name,
        "temperature": float(msg.temperature),
        "humidity": int(msg.humidity),
        "description": msg.description,
        "wind_speed": float(msg.wind_speed),
        "error": msg.error,
    }
