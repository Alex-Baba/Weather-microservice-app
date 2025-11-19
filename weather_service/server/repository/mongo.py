import os
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "weather_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "weather")

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[MONGO_DB]


def get_collection() -> Collection:
    return get_db()[MONGO_COLLECTION]


def insert_document(doc: dict):
    col = get_collection()
    return col.insert_one(doc).inserted_id


def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None
