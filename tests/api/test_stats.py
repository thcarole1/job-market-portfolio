import pytest
from fastapi.testclient import TestClient
from services.api.src.main import app

client = TestClient(app)

def test_get_stats_retourne_200():
    r = client.get("/stats/")
    assert r.status_code == 200

def test_get_stats_champs_obligatoires():
    r = client.get("/stats/")
    data = r.json()
    for champ in ["total", "par_contrat", "top_villes", "top_secteurs",
                  "par_experience", "top_metiers", "alternance", "evolution"]:
        assert champ in data

def test_get_stats_total_positif():
    r = client.get("/stats/")
    assert r.json()["total"] > 0

def test_get_stats_filtre_rome_label():
    r = client.get("/stats/", params={"rome_label": "Data Engineer"})
    assert r.status_code == 200
    assert r.json()["total"] >= 0
