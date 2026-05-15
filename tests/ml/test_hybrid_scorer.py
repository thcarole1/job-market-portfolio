"""
tests/ml/test_hybrid_scorer_skills.py
--------------------------------------
Tests unitaires pour HybridScorer._score_competences (hard + soft)
avec la nouvelle structure skills_extraits.

Lancer :
    PYTHONPATH=. pytest tests/ml/test_hybrid_scorer_skills.py -v
"""

import sys
from unittest.mock import MagicMock

# Modules du projet local absents de cet environnement de test
_mock_constants = MagicMock()
_mock_constants.COMPETENCES_CONNUES = ["Python", "Docker", "Elasticsearch", "Java", "Spring", "SQL", "PowerBI", "Power BI"]
_mock_constants.COORDS_VILLES = {"Paris": (48.85, 2.35)}
_mock_constants.FORMATION_SCORE = {"Bac+5": 5, "Bac+4": 4, "Bac+3": 3, "Bac+2": 2}

sys.modules.setdefault('services.ml.src.features', MagicMock(build_offer_text=lambda o: ''))
sys.modules.setdefault('services.ml.src.constants', _mock_constants)

import pytest
from services.ml.src.hybrid_scorer import HybridScorer, POIDS_COMPETENCES_INTERNES


@pytest.fixture
def scorer():
    return HybridScorer()


def _offre(hard=None, soft_exp=None, soft_imp=None, with_skills=True):
    """Construit une offre fictive avec ou sans skills_extraits."""
    o = {"title": "Data Engineer", "description": "offre test"}
    if with_skills:
        o["skills_extraits"] = {
            "hard_skills":     hard or ["Python", "Docker", "Elasticsearch"],
            "soft_explicites": soft_exp or ["Autonomie", "Rigueur"],
            "soft_implicites": soft_imp or ["Fiabilité"],
        }
    return o


def _cv(hard=None, soft=None):
    """Construit un CV structuré fictif."""
    return {
        "hard_skills":       hard or ["Python", "SQL"],
        "soft_skills":       soft or ["Autonomie", "Curiosité"],
        "annees_experience": 3,
        "localisation":      "Paris",
        "formation":         "Bac+5",
    }


# ── _score_hard_skills ────────────────────────────────────────────────────────

class TestScoreHardSkills:

    def test_match_partiel(self, scorer):
        cv = _cv(hard=["Python", "SQL"])
        offre = _offre(hard=["Python", "Docker", "Elasticsearch"])
        result = scorer._score_hard_skills(cv, offre)
        assert result["score"] == pytest.approx(1/3, abs=0.01)
        assert "Python" in result["match"]
        assert "Docker" in result["manquantes"]

    def test_match_parfait(self, scorer):
        cv = _cv(hard=["Python", "Docker", "Elasticsearch"])
        offre = _offre(hard=["Python", "Docker", "Elasticsearch"])
        result = scorer._score_hard_skills(cv, offre)
        assert result["score"] == 1.0
        assert result["manquantes"] == []

    def test_aucun_match(self, scorer):
        cv = _cv(hard=["Java", "Spring"])
        offre = _offre(hard=["Python", "Docker"])
        result = scorer._score_hard_skills(cv, offre)
        assert result["score"] == 0.0
        assert result["match"] == []

    def test_offre_sans_hard_skills(self, scorer):
        cv = _cv(hard=["Python"])
        # On force un offre avec skills_extraits mais hard_skills vide
        offre = {"title": "test", "description": "", "skills_extraits": {
            "hard_skills": [], "soft_explicites": [], "soft_implicites": []
        }}
        result = scorer._score_hard_skills(cv, offre)
        assert result["score"] == 0.0

    def test_fallback_sans_skills_extraits(self, scorer):
        """Sans skills_extraits, le fallback regex ne plante pas."""
        cv = _cv(hard=["Python"])
        offre = _offre(with_skills=False)
        result = scorer._score_hard_skills(cv, offre)
        assert "score" in result
        assert isinstance(result["score"], float)

    def test_normalisation_power_bi(self, scorer):
        """'Power BI' et 'PowerBI' doivent matcher."""
        cv = _cv(hard=["Power BI"])
        offre = _offre(hard=["PowerBI"])
        result = scorer._score_hard_skills(cv, offre)
        assert result["score"] == 1.0


# ── _score_soft_skills ────────────────────────────────────────────────────────

class TestScoreSoftSkills:

    def test_match_partiel(self, scorer):
        cv = _cv(soft=["Autonomie", "Curiosité"])
        offre = _offre(soft_exp=["Autonomie", "Rigueur"], soft_imp=["Fiabilité"])
        result = scorer._score_soft_skills(cv, offre)
        # offre = {autonomie, rigueur, fiabilité} → match = {autonomie}
        assert result["score"] == pytest.approx(1/3, abs=0.01)
        assert "autonomie" in result["match"]

    def test_match_parfait(self, scorer):
        cv = _cv(soft=["Autonomie", "Rigueur", "Fiabilité"])
        offre = _offre(soft_exp=["Autonomie", "Rigueur"], soft_imp=["Fiabilité"])
        result = scorer._score_soft_skills(cv, offre)
        assert result["score"] == 1.0

    def test_score_neutre_sans_soft_offre(self, scorer):
        """Offre sans soft skills → score neutre 0.5, pas de pénalité."""
        cv = _cv(soft=["Autonomie"])
        offre = {"title": "test", "description": "", "skills_extraits": {
            "hard_skills": ["Python"], "soft_explicites": [], "soft_implicites": []
        }}
        result = scorer._score_soft_skills(cv, offre)
        assert result["score"] == 0.5
        assert "note" in result

    def test_score_neutre_sans_skills_extraits(self, scorer):
        """Offre sans skills_extraits → score neutre 0.5."""
        cv = _cv(soft=["Autonomie"])
        offre = _offre(with_skills=False)
        result = scorer._score_soft_skills(cv, offre)
        assert result["score"] == 0.5
        assert "note" in result

    def test_cv_sans_soft_skills(self, scorer):
        # CV sans soft skills + offre avec soft skills → 0 match
        cv = {"hard_skills": [], "soft_skills": [], "annees_experience": 0,
              "localisation": "", "formation": ""}
        offre = {"title": "test", "description": "", "skills_extraits": {
            "hard_skills": [], "soft_explicites": ["Autonomie", "Rigueur"], "soft_implicites": []
        }}
        result = scorer._score_soft_skills(cv, offre)
        assert result["score"] == 0.0
        assert result["match"] == []


# ── _score_competences (global) ───────────────────────────────────────────────

class TestScoreCompetences:

    def test_structure_result(self, scorer):
        cv = _cv()
        offre = _offre()
        result = scorer._score_competences(cv, offre)
        assert "score" in result
        assert "hard" in result
        assert "soft" in result
        assert 0.0 <= result["score"] <= 1.0

    def test_ponderation_hard_soft(self, scorer):
        """Le score global respecte la pondération 70/30."""
        cv = _cv(
            hard=["Python", "Docker", "Elasticsearch"],
            soft=["Autonomie", "Rigueur", "Fiabilité"],
        )
        offre = _offre(
            hard=["Python", "Docker", "Elasticsearch"],
            soft_exp=["Autonomie", "Rigueur"],
            soft_imp=["Fiabilité"],
        )
        result = scorer._score_competences(cv, offre)
        expected = (
            result["hard"]["score"] * POIDS_COMPETENCES_INTERNES["hard"]
            + result["soft"]["score"] * POIDS_COMPETENCES_INTERNES["soft"]
        )
        assert result["score"] == pytest.approx(expected, abs=0.001)

    def test_score_final_integre(self, scorer):
        """score() complet ne plante pas avec la nouvelle structure."""
        import numpy as np
        cv = _cv()
        offre = _offre()
        embedding = np.ones((1, 768)) / 28.0  # vecteur unitaire approx
        result = scorer.score(cv, embedding, offre, embedding)
        assert "score_final" in result
        assert "detail" in result
        assert "competences" in result["detail"]
        assert "hard" in result["detail"]["competences"]
        assert "soft" in result["detail"]["competences"]
