import pytest
from fastapi.testclient import TestClient
from services.api.src.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_get_rome_labels():
    r = client.get("/offers/rome-labels")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0

def test_get_offer_inexistante():
    r = client.get("/offers/ID_INEXISTANT_XYZ")
    assert r.status_code == 404

def test_get_offers():
    r = client.get("/offers/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
