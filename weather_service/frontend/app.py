import logging
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from weather_service.server.providers.openweather import OpenWeatherProvider
from weather_service.server.providers.base import CityNotFoundError, ProviderError

logger = logging.getLogger("weather.frontend")


app = FastAPI(title="Weather Frontend")

# load .env automatically if present
load_dotenv()


class WeatherOut(BaseModel):
    city_name: str
    temperature: float
    humidity: int
    description: str | None = ""
    wind_speed: float


@app.get("/weather", response_model=WeatherOut)
def get_weather(city: str = Query(..., min_length=1)):
    try:
        provider = OpenWeatherProvider()
    except RuntimeError as e:
        logger.exception("Failed to initialize OpenWeatherProvider")
        raise HTTPException(status_code=500, detail=str(e))

    try:
        data = provider.fetch_weather(city)
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProviderError as e:
        logger.exception("Provider error while fetching weather")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in provider")
        raise HTTPException(status_code=500, detail="internal error")

    return {
        "city_name": data.get("city_name"),
        "temperature": data.get("temperature"),
        "humidity": data.get("humidity"),
        "description": data.get("description"),
        "wind_speed": data.get("wind_speed"),
    }


@app.get("/health")
def health():
    key = os.getenv("OPENWEATHER_API_KEY")
    return {"ok": True, "openweather_api_key_present": bool(key)}
