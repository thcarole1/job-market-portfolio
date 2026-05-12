import pytest
from services.ingestion.src.utils.normalizer import normalize_france_travail

@pytest.fixture
def offre_brute_minimale():
    return {
        "id":          "TEST123",
        "intitule":    "Data Engineer",
        "description": "Poste de data engineer.",
        "typeContrat": "CDI",
        "lieuTravail": {"libelle": "75 - Paris", "codePostal": "75001"},
        "dateCreation": "2026-01-01T00:00:00Z",
        "romeCode":    "M1811",
        "appellationlibelle": "Data Engineer",
    }

def test_normalize_retourne_dict(offre_brute_minimale):
    result = normalize_france_travail(offre_brute_minimale)
    assert isinstance(result, dict)

def test_normalize_champs_obligatoires(offre_brute_minimale):
    result = normalize_france_travail(offre_brute_minimale)
    for champ in ["id", "title", "source", "contract_type"]:
        assert champ in result

def test_normalize_source_france_travail(offre_brute_minimale):
    result = normalize_france_travail(offre_brute_minimale)
    assert result["source"] == "France_Travail"

def test_normalize_gere_champs_none():
    offre_minimale = {"id": "TEST456"}
    result = normalize_france_travail(offre_minimale)
    assert isinstance(result, dict)
    assert result["id"] == "TEST456"
