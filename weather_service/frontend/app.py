from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from weather_service.server.providers.openweather import OpenWeatherProvider

app = FastAPI(title="Weather Frontend")


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
        raise HTTPException(status_code=500, detail=str(e))

    try:
        data = provider.fetch_weather(city)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "city_name": data.get("city_name"),
        "temperature": data.get("temperature"),
        "humidity": data.get("humidity"),
        "description": data.get("description"),
        "wind_speed": data.get("wind_speed"),
    }
