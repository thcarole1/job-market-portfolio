import pytest
import numpy as np
from services.ml.src.hybrid_scorer import HybridScorer, _normalize

scorer = HybridScorer()

# ── Fixtures ──────────────────────────────────────────

@pytest.fixture
def cv_structured_complet():
    return {
        "competences":       ["Python", "SQL", "Spark"],
        "annees_experience": 5,
        "localisation":      "Paris",
        "formation":         "Master"
    }

@pytest.fixture
def offre_matching():
    return {
        "title":              "Data Engineer",
        "description":        "Nous recherchons un expert Python SQL Spark.",
        "experience_label":   "3 An(s)",
        "workplace_label":    "75 - Paris",
        "workplace_postal_code": "75001",
        "formation_requise":  "Master",
        "competences":        [],
        "languages":          [],
        "professional_qualities": []
    }

@pytest.fixture
def embedding_dummy():
    v = np.random.rand(1, 768).astype(np.float32)
    return v / np.linalg.norm(v)

# ── Tests _normalize ──────────────────────────────────

def test_normalize_power_bi():
    assert _normalize("Power BI") == "powerbi"

def test_normalize_scikit_learn():
    assert _normalize("scikit-learn") == "scikitlearn"

def test_normalize_casse():
    assert _normalize("Python") == "python"

# ── Tests _score_competences ──────────────────────────

def test_score_competences_perfect_match(cv_structured_complet, offre_matching):
    result = scorer._score_competences(cv_structured_complet, offre_matching)
    assert result["score"] >= 0.0
    assert result["score"] <= 1.0
    assert isinstance(result["match"], list)
    assert isinstance(result["manquantes"], list)

def test_score_competences_no_competences_in_offre(cv_structured_complet):
    offre_vide = {
        "title": "Poste générique",
        "description": "Nous recrutons.",
        "competences": [], "languages": [], "professional_qualities": []
    }
    result = scorer._score_competences(cv_structured_complet, offre_vide)
    assert result["score"] == 0.0
    assert result["offre"] == []

# ── Tests _score_experience ───────────────────────────

def test_score_experience_suffisante(cv_structured_complet, offre_matching):
    result = scorer._score_experience(cv_structured_complet, offre_matching)
    assert result["score"] == 1.0
    assert result["cv"] == 5
    assert result["offre"] == 3

def test_score_experience_insuffisante():
    cv = {"annees_experience": 1}
    offre = {"experience_label": "5 An(s)"}
    result = scorer._score_experience(cv, offre)
    assert result["score"] == 0.0
    assert result["manquantes"] == 4

def test_score_experience_non_precisee():
    cv = {"annees_experience": 3}
    offre = {"experience_label": ""}
    result = scorer._score_experience(cv, offre)
    assert result["score"] == 1.0
    assert result["offre"] is None

# ── Tests _score_localisation ─────────────────────────

def test_score_localisation_match(cv_structured_complet, offre_matching):
    result = scorer._score_localisation(cv_structured_complet, offre_matching)
    assert result["score"] == 1.0

def test_score_localisation_non_precise():
    cv = {"localisation": "Non précisé"}
    offre = {"workplace_label": "75 - Paris", "workplace_postal_code": "75001",
             "workplace_latitude": None, "workplace_longitude": None}
    result = scorer._score_localisation(cv, offre)
    assert result["score"] == 0.5

def test_score_localisation_different():
    cv = {"localisation": "Lyon"}
    offre = {"workplace_label": "75 - Paris", "workplace_postal_code": "75001",
             "workplace_latitude": None, "workplace_longitude": None}
    result = scorer._score_localisation(cv, offre)
    assert result["score"] == 0.0

# ── Tests _score_formation ────────────────────────────

def test_score_formation_suffisante(cv_structured_complet, offre_matching):
    result = scorer._score_formation(cv_structured_complet, offre_matching)
    assert result["score"] == 1.0

def test_score_formation_insuffisante():
    cv = {"formation": "Bac"}
    offre = {"formation_requise": "Master"}
    result = scorer._score_formation(cv, offre)
    assert result["score"] == 0.0

def test_score_formation_non_precisee():
    cv = {"formation": "Master"}
    offre = {"formation_requise": ""}
    result = scorer._score_formation(cv, offre)
    assert result["score"] == 1.0

# ── Tests score global ────────────────────────────────

def test_score_final_entre_0_et_1(cv_structured_complet, offre_matching, embedding_dummy):
    result = scorer.score(cv_structured_complet, embedding_dummy, offre_matching, embedding_dummy)
    assert 0.0 <= result["score_final"] <= 1.0
    assert "detail" in result
    assert "sbert" in result["detail"]
