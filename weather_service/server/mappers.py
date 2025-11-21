from typing import Dict
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from generated.proto import weather_pb2


def dict_to_weather_response(data: Dict) -> weather_pb2.WeatherResponse:
    """Convert a normalized weather dict to a protobuf WeatherResponse."""
    msg = weather_pb2.WeatherResponse(
        city_name=data.get("city_name", ""),
        temperature=float(data.get("temperature", 0.0)),
        humidity=int(data.get("humidity", 0)),
        description=str(data.get("description", "")),
        wind_speed=float(data.get("wind_speed", 0.0)),
    )

    fa = data.get("fetched_at")
    if isinstance(fa, datetime):
        # If fetched_at is timezone-aware local time, convert to UTC for the protobuf Timestamp
        if fa.tzinfo is not None:
            fa_utc = fa.astimezone(timezone.utc)
        else:
            fa_utc = fa
        ts = Timestamp()
        ts.FromDatetime(fa_utc)
        msg.fetched_at.CopyFrom(ts)

    return msg


def weather_response_to_dict(msg: weather_pb2.WeatherResponse) -> Dict:
    """Convert a protobuf WeatherResponse to a plain dict."""
    out = {
        "city_name": msg.city_name,
        "temperature": float(msg.temperature),
        "humidity": int(msg.humidity),
        "description": msg.description,
        "wind_speed": float(msg.wind_speed),
    }

    if msg.HasField("fetched_at"):
        out["fetched_at"] = msg.fetched_at.ToDatetime()
    else:
        out["fetched_at"] = None

    return out
