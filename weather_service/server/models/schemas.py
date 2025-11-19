from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: Optional[str]
    GRPC_API_KEY: str = Field(default="secret123")
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="weather_db")
    MONGO_COLLECTION: str = Field(default="weather")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


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
