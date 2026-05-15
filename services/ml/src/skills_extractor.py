"""
skills_extractor.py
-------------------
Extraction de hard skills et soft skills depuis le texte d'une offre d'emploi
par similarité cosine SBERT (approche zero-shot).

Principe :
  1. Les phrases-référence (SOFT_SKILLS_REFERENCES) sont encodées UNE SEULE FOIS
     à l'instanciation du SkillsExtractor (singleton).
  2. Pour chaque offre, les phrases du texte sont encodées en batch.
  3. Pour chaque paire (phrase_offre, phrase_référence), on calcule la similarité
     cosine. Si elle dépasse le seuil, le skill associé est détecté.
  4. Le résultat est dédupliqué et structuré par catégorie.

Usage batch (script nocturne) :
    extractor = SkillsExtractor()
    result = extractor.extract(offre["description"])
    # → {"hard_skills": [...], "soft_explicites": [...], "soft_implicites": [...]}

Usage recommandation (enrichissement à la volée) :
    # Même interface, même singleton.
    result = extractor.extract(offre["description"], offre.get("title", ""))
"""

from __future__ import annotations

import re
import logging
from functools import lru_cache
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import des constantes — on importe depuis constants.py existant
# et depuis l'extension soft skills.
# En production : fusionner constants_soft_skills_extension dans constants.py
# ---------------------------------------------------------------------------
try:
    from services.ml.src.constants import COMPETENCES_CONNUES
except ImportError:
    # Fallback pour les tests unitaires lancés directement
    COMPETENCES_CONNUES: list[str] = []

try:
    from services.ml.src.constants import (
        SOFT_SKILLS_REFERENCES,
        SOFT_SKILLS_LABELS_FR,
        SOFT_SKILLS_CATEGORIES,
    )
except ImportError:
    from constants_soft_skills_extension import (  # type: ignore
        SOFT_SKILLS_REFERENCES,
        SOFT_SKILLS_LABELS_FR,
        SOFT_SKILLS_CATEGORIES,
    )


# ---------------------------------------------------------------------------
# Helpers texte
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _split_sentences(text: str) -> list[str]:
    """
    Découpe un texte en phrases non vides de longueur raisonnable.

    v2 — sous-découpe les phrases longues sur les virgules pour éviter
    la dilution sémantique SBERT sur les phrases multi-idées.
    Exemple : "excellentes capacités de communication, travailler avec
    des équipes pluridisciplinaires" → 2 phrases distinctes.
    """
    if not text:
        return []

    raw = _SENTENCE_SPLIT_RE.split(text.strip())

    sentences = []
    for s in raw:
        s = s.strip().lstrip("-•·→▪ ").strip()
        if not s:
            continue

        words = s.split()

        # Sous-découpe sur virgules si la phrase dépasse 15 mots
        if len(words) > 15 and "," in s:
            parts = [p.strip() for p in s.split(",")]
            for p in parts:
                if len(p.split()) >= 4:
                    sentences.append(p)
        else:
            if 4 <= len(words) <= 60:
                sentences.append(s)

    return sentences


def _extract_hard_skills_by_lexicon(text: str) -> list[str]:
    """
    Détection de hard skills par regex sur le lexique COMPETENCES_CONNUES.
    Réplique la logique de normalizer.py pour rester cohérent.
    Retourne une liste dédupliquée de compétences détectées.
    """
    text_lower = text.lower()
    found = set()
    for competence in COMPETENCES_CONNUES:
        pattern = r"\b" + re.escape(competence.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(competence)
    return sorted(found)


# ---------------------------------------------------------------------------
# SkillsExtractor
# ---------------------------------------------------------------------------

class SkillsExtractor:
    """
    Extracteur de skills par SBERT zero-shot.

    Paramètres
    ----------
    threshold : float
        Seuil de similarité cosine pour valider un skill (défaut : 0.75).
    model_name : str
        Modèle sentence-transformers à utiliser.
        Doit être le même que celui utilisé pour les embeddings d'offres.
    """

    _instance: "SkillsExtractor | None" = None

    def __init__(
        self,
        threshold: float = 0.75,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    ) -> None:
        self.threshold = threshold
        self.model_name = model_name
        self._model = None
        self._ref_embeddings: dict[str, np.ndarray] = {}
        self._ref_labels: dict[str, list[str]] = {}
        self._initialized = False

    # -- Singleton ------------------------------------------------------------

    @classmethod
    def get_instance(
        cls,
        threshold: float = 0.75,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    ) -> "SkillsExtractor":
        """Retourne le singleton, en le créant si nécessaire."""
        if cls._instance is None:
            cls._instance = cls(threshold=threshold, model_name=model_name)
        return cls._instance

    # -- Initialisation -------------------------------------------------------

    def _load_model(self) -> None:
        """Charge le modèle SBERT (lazy loading)."""
        if self._model is not None:
            return
        try:
            # Réutilise le singleton encoder existant si disponible
            from services.ml.src.encoder import get_model  # type: ignore
            self._model = get_model()
            logger.info("SkillsExtractor : modèle chargé via encoder.get_model()")
        except ImportError:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"SkillsExtractor : modèle chargé directement ({self.model_name})")

    def initialize(self) -> None:
        """
        Pré-calcule les embeddings de toutes les phrases-référence.
        À appeler UNE SEULE FOIS au démarrage du script batch ou de l'API.
        Durée estimée : 2–5 secondes selon le matériel.
        """
        if self._initialized:
            return

        self._load_model()
        logger.info("SkillsExtractor : calcul des embeddings de référence...")

        for skill_key, phrases in SOFT_SKILLS_REFERENCES.items():
            embeddings = self._model.encode(
                phrases,
                batch_size=32,
                normalize_embeddings=True,  # L2-norm → cosine = dot product
                show_progress_bar=False,
            )
            self._ref_embeddings[skill_key] = embeddings  # shape (n_phrases, 768)
            self._ref_labels[skill_key] = phrases

        self._initialized = True
        n_phrases = sum(len(v) for v in SOFT_SKILLS_REFERENCES.values())
        logger.info(
            f"SkillsExtractor initialisé : {len(SOFT_SKILLS_REFERENCES)} skills, "
            f"{n_phrases} phrases-référence encodées."
        )

    # -- Extraction -----------------------------------------------------------

    def extract(
        self,
        description: str,
        title: str = "",
        threshold: float | None = None,
    ) -> dict[str, Any]:
        """
        Extrait les skills depuis le texte d'une offre.

        Paramètres
        ----------
        description : str
            Texte complet de l'offre (description, profil recherché...).
        title : str
            Intitulé du poste — ajouté au corpus pour améliorer la détection.
        threshold : float | None
            Seuil de similarité. Si None, utilise self.threshold.

        Retourne
        --------
        dict avec les clés :
            hard_skills       : list[str]  — compétences techniques détectées
            soft_explicites   : list[str]  — soft skills explicites détectés
            soft_implicites   : list[str]  — soft skills inférés par contexte
            scores            : dict[str, float]  — score max par skill détecté
            methode           : str
            seuil             : float
            version           : str
        """
        if not self._initialized:
            self.initialize()

        seuil = threshold if threshold is not None else self.threshold

        # 1. Hard skills : lexique exact (rapide, déterministe)
        full_text = f"{title} {description}".strip()
        hard_skills = _extract_hard_skills_by_lexicon(full_text)

        # 2. Soft skills : SBERT zero-shot
        sentences = _split_sentences(full_text)
        if not sentences:
            return self._empty_result(hard_skills, seuil)

        # Encode toutes les phrases de l'offre en batch (L2-normalisé)
        offer_embeddings = self._model.encode(
            sentences,
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=False,
        )  # shape (n_sentences, 768)

        soft_explicites: list[str] = []
        soft_implicites: list[str] = []
        scores: dict[str, float] = {}

        for skill_key, ref_emb in self._ref_embeddings.items():
            # Similarité cosine = dot product (embeddings L2-normalisés)
            # sim_matrix shape : (n_sentences, n_ref_phrases)
            sim_matrix = offer_embeddings @ ref_emb.T

            # Score du skill = max sur toutes les paires (phrase_offre, phrase_ref)
            max_score = float(sim_matrix.max())

            if max_score >= seuil:
                label = SOFT_SKILLS_LABELS_FR.get(skill_key, skill_key)
                scores[skill_key] = round(max_score, 4)

                # Classification explicite / implicite
                # Les implicites sont ceux qui ne sont pas directement nommés
                # dans l'offre mais inférés par contexte sémantique
                if skill_key in ("fiabilite", "sens_critique"):
                    soft_implicites.append(label)
                else:
                    soft_explicites.append(label)

        return {
            "hard_skills": hard_skills,
            "soft_explicites": sorted(soft_explicites),
            "soft_implicites": sorted(soft_implicites),
            "scores": scores,
            "methode": "sbert_zero_shot",
            "seuil": seuil,
            "version": "1.0",
        }

    def _empty_result(self, hard_skills: list[str], seuil: float) -> dict[str, Any]:
        return {
            "hard_skills": hard_skills,
            "soft_explicites": [],
            "soft_implicites": [],
            "scores": {},
            "methode": "sbert_zero_shot",
            "seuil": seuil,
            "version": "1.0",
        }

    # -- Utilitaire gap CV/offre ----------------------------------------------

    def compute_gap(
        self,
        cv_skills: list[str],
        offer_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Compare les skills du CV avec ceux détectés dans une offre.

        Paramètres
        ----------
        cv_skills : list[str]
            Skills extraits du CV (via CVStructurer).
        offer_result : dict
            Résultat de extract() pour l'offre cible.

        Retourne
        --------
        dict avec :
            maitrise      : list[str]  — skills présents dans CV et offre
            manquants     : list[str]  — skills requis par l'offre absents du CV
            bonus         : list[str]  — skills du CV non requis par l'offre
            taux_match    : float      — % de skills offre couverts par le CV
            recommandations : list[str]
        """
        cv_lower = {s.lower() for s in cv_skills}

        offre_hard = {s.lower() for s in offer_result.get("hard_skills", [])}
        offre_soft = {
            s.lower()
            for s in (
                offer_result.get("soft_explicites", [])
                + offer_result.get("soft_implicites", [])
            )
        }
        offre_all = offre_hard | offre_soft

        maitrise = sorted(offre_all & cv_lower)
        manquants = sorted(offre_all - cv_lower)
        bonus = sorted(cv_lower - offre_all)

        taux_match = (
            round(len(maitrise) / len(offre_all) * 100, 1)
            if offre_all
            else 0.0
        )

        recommandations = _build_recommendations(manquants, taux_match)

        return {
            "maitrise": maitrise,
            "manquants": manquants,
            "bonus": bonus,
            "taux_match": taux_match,
            "recommandations": recommandations,
        }


# ---------------------------------------------------------------------------
# Génération de recommandations textuelles simples
# ---------------------------------------------------------------------------

def _build_recommendations(manquants: list[str], taux_match: float) -> list[str]:
    """Génère des recommandations textuelles à partir des skills manquants."""
    recs = []

    if taux_match >= 80:
        recs.append("Votre profil correspond bien à cette offre.")
    elif taux_match >= 50:
        recs.append(
            f"Votre profil couvre {taux_match}% des compétences requises. "
            "Quelques points de développement identifiés ci-dessous."
        )
    else:
        recs.append(
            f"Votre profil couvre {taux_match}% des compétences requises. "
            "Un plan de développement ciblé est recommandé avant de postuler."
        )

    # Recommandations par skill manquant
    _SKILL_TIPS: dict[str, str] = {
        "autonomie": (
            "Autonomie : valorisez vos projets personnels ou contributions open-source "
            "dans votre CV pour démontrer votre capacité à vous organiser seul."
        ),
        "travail en équipe": (
            "Travail en équipe : mentionnez les collaborations concrètes (code review, "
            "projets collectifs, méthodes agiles) dans vos expériences."
        ),
        "communication": (
            "Communication : préparez un exemple concret où vous avez expliqué "
            "un sujet technique à un non-technicien."
        ),
        "rigueur": (
            "Rigueur : mettez en avant vos tests unitaires, votre documentation "
            "et vos pratiques de qualité logicielle."
        ),
        "curiosité": (
            "Curiosité : listez vos formations récentes, certifications ou "
            "projets d'auto-apprentissage."
        ),
        "gestion du stress": (
            "Gestion du stress : illustrez votre capacité à livrer dans les délais "
            "avec un exemple de projet sous contrainte."
        ),
        "sens du résultat": (
            "Sens du résultat : chiffrez vos réalisations passées "
            "(volume de données traitées, temps de traitement réduit, etc.)."
        ),
        "adaptabilité": (
            "Adaptabilité : évoquez un contexte où vous avez dû changer d'approche "
            "ou apprendre rapidement un nouvel outil."
        ),
        "fiabilité": (
            "Fiabilité : insistez sur votre couverture de tests et votre gestion "
            "des incidents ou imprévus dans vos projets."
        ),
        "sens critique": (
            "Sens critique : donnez un exemple où vous avez détecté une anomalie "
            "dans les données ou remis en question une hypothèse."
        ),
    }

    for skill in manquants[:5]:  # max 5 recommandations
        tip = _SKILL_TIPS.get(skill.lower())
        if tip:
            recs.append(tip)
        else:
            recs.append(
                f"{skill.capitalize()} : identifiez une formation ou expérience "
                "pour développer cette compétence."
            )

    return recs
