import pytest
from fastapi.testclient import TestClient
from services.api.src.main import app

client = TestClient(app)

def test_recommend_tfidf():
    r = client.post("/recommend/", json={"query": "Data Engineer Python SQL", "top_n": 5},
                    params={"model": "tfidf"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_recommend_filtre_sans_resultat():
    r = client.post("/recommend/",
                    json={"query": "Data Engineer", "top_n": 5,
                          "contract_type": "XXXXX"},
                    params={"model": "tfidf"})
    assert r.status_code == 200
    assert r.json() == []

def test_recommend_cv_format_invalide():
    r = client.post("/recommend/cv",
                    files={"file": ("test.txt", b"contenu", "text/plain")},
                    params={"model": "tfidf", "top_n": 5})
    assert r.status_code == 422
