import datetime
import mongomock
import pytest

from weather_service.server.repository import mongo as repo_module


@pytest.fixture
def mock_client(monkeypatch):
    client = mongomock.MongoClient()
    # Monkeypatch the module-level _client in the real repo module
    monkeypatch.setattr(repo_module, "_client", client)
    return client


def test_insert_and_find_documents(mock_client):
    

    record = {
        "city_name": "Testville",
        "temperature": 21.5,
        "humidity": 60,
        "description": "clear sky",
        "wind_speed": 3.2,
        "fetched_at": datetime.datetime(2025, 11, 20, 12, 0, 0),
    }

    inserted_id = repo_module.insert_document(record)
    assert inserted_id is not None

    results = repo_module.find_documents({"city_name": "Testville"}, limit=10)
    assert isinstance(results, list)
    assert len(results) == 1
    r = results[0]
    assert r["city_name"] == record["city_name"]
    assert abs(r["temperature"] - record["temperature"]) < 1e-6
    assert isinstance(r["fetched_at"], datetime.datetime)


def test_find_documents_no_results(mock_client):
    results = repo_module.find_documents({"city_name": "Nowhere"})
    assert results == []
