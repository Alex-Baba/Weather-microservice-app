from __future__ import annotations
from datetime import datetime
from typing import Optional

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# load .env if present
load_dotenv()


class Settings:
    def __init__(self):
        self.OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
        self.GRPC_API_KEY: str = os.getenv("GRPC_API_KEY", "secret123")
        self.MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.MONGO_DB: str = os.getenv("MONGO_DB", "weather_db")
        self.MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "weather")


class WeatherData(BaseModel):
    city_name: str
    temperature: float
    humidity: int
    description: Optional[str] = ""
    wind_speed: float = 0.0
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_openweather(cls, data: dict) -> "WeatherData":
        main = data.get("main", {}) or {}
        weather = (data.get("weather") or [{}])[0] or {}
        wind = data.get("wind", {}) or {}
        return cls(
            city_name=data.get("name", ""),
            temperature=float(main.get("temp", 0.0)),
            humidity=int(main.get("humidity", 0)),
            description=str(weather.get("description", "")),
            wind_speed=float(wind.get("speed", 0.0)),
        )
