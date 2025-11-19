from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection

from weather_service.server.config import settings

MONGO_URI = settings.MONGO_URI
MONGO_DB = settings.MONGO_DB
MONGO_COLLECTION = settings.MONGO_COLLECTION

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
