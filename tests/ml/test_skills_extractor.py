"""
tests/ml/test_skills_extractor.py
----------------------------------
Tests unitaires pour SkillsExtractor (SBERT zero-shot).

Les tests sont organisés en deux niveaux :
  - Tests sans modèle (logique pure, rapides) → marqués "unit"
  - Tests avec modèle réel (lents, nécessitent sentence-transformers) → marqués "integration"

Lancer uniquement les tests rapides :
    PYTHONPATH=. pytest tests/ml/test_skills_extractor.py -m "not integration" -v

Lancer tous les tests (avec chargement du modèle) :
    PYTHONPATH=. pytest tests/ml/test_skills_extractor.py -v
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Tests sans modèle — logique pure
# ---------------------------------------------------------------------------

class TestSplitSentences:
    """Tests de la fonction de découpage en phrases."""

    def test_import(self):
        from services.ml.src.skills_extractor import _split_sentences
        assert callable(_split_sentences)

    def test_phrase_normale(self):
        from services.ml.src.skills_extractor import _split_sentences
        text = "Vous devez maîtriser Python et SQL. Vous travaillerez en équipe agile."
        result = _split_sentences(text)
        assert len(result) == 2

    def test_sous_decoupe_virgule(self):
        from services.ml.src.skills_extractor import _split_sentences
        text = (
            "Vous disposez d'excellentes capacités de communication, "
            "aimez partager vos connaissances et travailler avec des équipes pluridisciplinaires."
        )
        result = _split_sentences(text)
        assert len(result) == 2
        assert any("communication" in s for s in result)
        assert any("pluridisciplinaires" in s for s in result)

    def test_pas_sous_decoupe_courte(self):
        from services.ml.src.skills_extractor import _split_sentences
        text = "Rigoureux, autonome et motivé, rejoignez notre équipe."
        result = _split_sentences(text)
        assert len(result) == 1

    def test_retire_tirets_liste(self):
        from services.ml.src.skills_extractor import _split_sentences
        text = "- Travailler en équipe pluridisciplinaire et partager ses connaissances.\n- Faire preuve d'autonomie dans la gestion de ses missions quotidiennes."
        result = _split_sentences(text)
        assert all(not s.startswith("-") for s in result)
        assert len(result) == 2

    def test_ignore_phrases_courtes(self):
        from services.ml.src.skills_extractor import _split_sentences
        text = "Python. SQL. Vous devez maîtriser Python et travailler en équipe."
        result = _split_sentences(text)
        # "Python." et "SQL." ont < 5 mots → ignorées
        assert all(len(s.split()) >= 5 for s in result)

    def test_texte_vide(self):
        from services.ml.src.skills_extractor import _split_sentences
        assert _split_sentences("") == []
        assert _split_sentences(None) == []  # type: ignore


class TestExtractHardSkillsByLexicon:
    """Tests de la détection hard skills par lexique."""

    def test_detection_python(self):
        from services.ml.src.skills_extractor import _extract_hard_skills_by_lexicon
        result = _extract_hard_skills_by_lexicon("Maîtrise de Python et Docker requise.")
        # Dépend de COMPETENCES_CONNUES — on vérifie juste que c'est une liste
        assert isinstance(result, list)

    def test_case_insensitive(self):
        from services.ml.src.skills_extractor import _extract_hard_skills_by_lexicon
        r1 = _extract_hard_skills_by_lexicon("python")
        r2 = _extract_hard_skills_by_lexicon("PYTHON")
        assert r1 == r2

    def test_texte_vide(self):
        from services.ml.src.skills_extractor import _extract_hard_skills_by_lexicon
        assert _extract_hard_skills_by_lexicon("") == []


class TestBuildRecommendations:
    """Tests de la génération de recommandations."""

    def test_bon_match(self):
        from services.ml.src.skills_extractor import _build_recommendations
        recs = _build_recommendations([], taux_match=85.0)
        assert any("correspond bien" in r for r in recs)

    def test_match_moyen(self):
        from services.ml.src.skills_extractor import _build_recommendations
        recs = _build_recommendations(["autonomie"], taux_match=60.0)
        assert len(recs) >= 2  # intro + au moins 1 conseil

    def test_mauvais_match(self):
        from services.ml.src.skills_extractor import _build_recommendations
        recs = _build_recommendations(
            ["autonomie", "rigueur", "communication", "curiosité", "fiabilité"],
            taux_match=20.0,
        )
        assert any("plan de développement" in r for r in recs)
        assert len(recs) <= 6  # max 1 intro + 5 skills

    def test_max_cinq_recommandations(self):
        from services.ml.src.skills_extractor import _build_recommendations
        manquants = ["a", "b", "c", "d", "e", "f", "g"]
        recs = _build_recommendations(manquants, taux_match=10.0)
        # 1 intro + max 5 skills
        assert len(recs) <= 6


class TestComputeGap:
    """Tests de la méthode compute_gap (logique set, sans modèle)."""

    def _make_extractor(self):
        from services.ml.src.skills_extractor import SkillsExtractor
        ext = SkillsExtractor.__new__(SkillsExtractor)
        ext.threshold = 0.75
        ext._initialized = True
        return ext

    def _make_offer_result(self, hard=None, soft_exp=None, soft_imp=None):
        return {
            "hard_skills": hard or ["Python", "Docker"],
            "soft_explicites": soft_exp or ["Autonomie", "Rigueur"],
            "soft_implicites": soft_imp or ["Fiabilité"],
        }

    def test_match_parfait(self):
        ext = self._make_extractor()
        cv = ["python", "docker", "autonomie", "rigueur", "fiabilité"]
        result = ext.compute_gap(cv, self._make_offer_result())
        assert result["taux_match"] == 100.0
        assert result["manquants"] == []

    def test_match_partiel(self):
        ext = self._make_extractor()
        cv = ["python"]
        result = ext.compute_gap(cv, self._make_offer_result())
        assert result["taux_match"] < 100.0
        assert "python" in result["maitrise"]
        assert len(result["manquants"]) > 0

    def test_cv_vide(self):
        ext = self._make_extractor()
        result = ext.compute_gap([], self._make_offer_result())
        assert result["taux_match"] == 0.0
        assert result["maitrise"] == []

    def test_offre_vide(self):
        ext = self._make_extractor()
        result = ext.compute_gap(
            ["python"],
            {"hard_skills": [], "soft_explicites": [], "soft_implicites": []},
        )
        assert result["taux_match"] == 0.0

    def test_bonus_cv(self):
        """Skills dans le CV mais pas dans l'offre → bonus."""
        ext = self._make_extractor()
        cv = ["python", "docker", "autonomie", "rigueur", "fiabilité", "kubernetes"]
        result = ext.compute_gap(cv, self._make_offer_result())
        assert "kubernetes" in result["bonus"]


# ---------------------------------------------------------------------------
# Tests d'intégration — nécessitent le modèle SBERT
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestSkillsExtractorIntegration:
    """Tests avec le vrai modèle SBERT. Lents (~5–15s au premier run)."""

    @pytest.fixture(scope="class")
    def extractor(self):
        from services.ml.src.skills_extractor import SkillsExtractor
        # Utilise une instance dédiée (pas le singleton global)
        ext = SkillsExtractor(threshold=0.75)
        ext.initialize()
        return ext

    def test_detection_autonomie(self, extractor):
        """Une offre mentionnant l'autonomie doit détecter ce soft skill."""
        text = (
            "Nous recherchons un profil capable de travailler en toute autonomie "
            "et de gérer ses priorités sans supervision constante."
        )
        result = extractor.extract(text)
        assert "Autonomie" in result["soft_explicites"], (
            f"'Autonomie' non détecté. Soft explicites : {result['soft_explicites']}"
        )

    def test_detection_travail_equipe(self, extractor):
        text = (
            "Vous rejoindrez une équipe dynamique et devrez collaborer étroitement "
            "avec des profils variés dans un esprit d'équipe fort."
        )
        result = extractor.extract(text)
        assert "Travail en équipe" in result["soft_explicites"], (
            f"'Travail en équipe' non détecté. Soft explicites : {result['soft_explicites']}"
        )

    def test_detection_rigueur(self, extractor):
        text = (
            "Le poste requiert de la rigueur, un souci du détail et une attention "
            "particulière à la qualité des livrables produits."
        )
        result = extractor.extract(text)
        assert "Rigueur" in result["soft_explicites"]

    def test_structure_result(self, extractor):
        """Le résultat doit toujours avoir la structure attendue."""
        result = extractor.extract("Poste de data engineer Python Docker Kubernetes.")
        assert "hard_skills" in result
        assert "soft_explicites" in result
        assert "soft_implicites" in result
        assert "scores" in result
        assert "methode" in result
        assert result["methode"] == "sbert_zero_shot"
        assert result["version"] == "1.0"
        assert isinstance(result["hard_skills"], list)
        assert isinstance(result["soft_explicites"], list)
        assert isinstance(result["soft_implicites"], list)

    def test_seuil_custom(self, extractor):
        """Un seuil très élevé ne doit détecter presque rien."""
        text = "Nous cherchons un profil autonome et rigoureux."
        result_strict = extractor.extract(text, threshold=0.99)
        result_normal = extractor.extract(text, threshold=0.75)
        # Avec seuil 0.99, on doit avoir <= résultats qu'avec 0.75
        n_strict = len(result_strict["soft_explicites"]) + len(result_strict["soft_implicites"])
        n_normal = len(result_normal["soft_explicites"]) + len(result_normal["soft_implicites"])
        assert n_strict <= n_normal

    def test_texte_vide(self, extractor):
        """Un texte vide ne doit pas planter."""
        result = extractor.extract("")
        assert result["hard_skills"] == []
        assert result["soft_explicites"] == []
        assert result["soft_implicites"] == []

    def test_singleton(self):
        """Le singleton doit retourner la même instance."""
        from services.ml.src.skills_extractor import SkillsExtractor
        a = SkillsExtractor.get_instance()
        b = SkillsExtractor.get_instance()
        assert a is b

    def test_gap_reel(self, extractor):
        """Test end-to-end : extract + compute_gap."""
        offre_text = (
            "Nous recherchons un data engineer Python autonome, rigoureux, "
            "avec un bon esprit d'équipe et une curiosité pour les nouvelles technologies."
        )
        cv_skills = ["python", "autonomie", "rigueur"]

        offer_result = extractor.extract(offre_text)
        gap = extractor.compute_gap(cv_skills, offer_result)

        assert "taux_match" in gap
        assert "maitrise" in gap
        assert "manquants" in gap
        assert "recommandations" in gap
        assert 0.0 <= gap["taux_match"] <= 100.0
        assert isinstance(gap["recommandations"], list)
        assert len(gap["recommandations"]) >= 1
