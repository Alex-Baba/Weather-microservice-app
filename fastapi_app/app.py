import logging
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from weather_service.server.providers.openweather import OpenWeatherProvider
from weather_service.server.providers.base import CityNotFoundError, ProviderError
from weather_service.server.repository import mongo as repo_mongo
from datetime import datetime
from bson import ObjectId
from weather_service.server import storage

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
    fetched_at: str | None = None


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

    # persist the fetched weather (best-effort)
    try:
        storage.save_weather(data)
    except Exception:
        logger.exception("Failed to save weather to DB")

    # convert fetched_at to ISO string if present
    fa = data.get("fetched_at")
    if isinstance(fa, datetime):
        fa_iso = fa.isoformat()
    else:
        fa_iso = fa

    return {
        "city_name": data.get("city_name"),
        "temperature": data.get("temperature"),
        "humidity": data.get("humidity"),
        "description": data.get("description"),
        "wind_speed": data.get("wind_speed"),
        "fetched_at": fa_iso,
    }


@app.get("/health")
def health():
    key = os.getenv("OPENWEATHER_API_KEY")
    return {"ok": True, "openweather_api_key_present": bool(key)}


@app.get("/history")
def history(city: str | None = Query(None), limit: int = Query(50, ge=1, le=1000)):
    flt = {}
    if city:
        flt["city_name"] = city

    try:
        docs = repo_mongo.find_documents(filter=flt, limit=limit)
    except Exception as e:
        logger.exception("DB error fetching history")
        raise HTTPException(status_code=500, detail="db error")

    def serialize(doc: dict):
        out = {k: v for k, v in doc.items() if k != "_id"}
        out["id"] = str(doc.get("_id"))
        fa = doc.get("fetched_at")
        if isinstance(fa, datetime):
            out["fetched_at"] = fa.isoformat()
        else:
            out["fetched_at"] = fa
        return out

    return [serialize(d) for d in docs]
