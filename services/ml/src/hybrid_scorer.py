import re
import logging
from math import radians, sin, cos, sqrt, atan2
from sklearn.metrics.pairwise import cosine_similarity
from services.ml.src.features import build_offer_text

logger = logging.getLogger(__name__)

from services.ml.src.constants import (
    COMPETENCES_CONNUES,
    COORDS_VILLES,
    FORMATION_SCORE
)

# ── Pondérations ──────────────────────────────────────
POIDS = {
    "sbert":        0.40,
    "competences":  0.30,
    "experience":   0.15,
    "localisation": 0.10,
    "formation":    0.05
}

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en km entre deux points GPS (formule de Haversine)."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return round(2 * R * atan2(sqrt(a), sqrt(1 - a)), 1)

def _normalize(c: str) -> str:
    """Normalise une compétence pour comparaison : minuscules, sans espaces."""
    return c.lower().replace(" ", "").replace("-", "")


class HybridScorer:

    def score(self, cv_structured: dict, cv_embedding,
              offre: dict, offre_embedding) -> dict:
        """
        Calcule le score hybride entre un CV et une offre.
        Retourne un dict avec score_final et le détail enrichi par critère.
        """
        competences_detail  = self._score_competences(cv_structured, offre)
        experience_detail   = self._score_experience(cv_structured, offre)
        localisation_detail = self._score_localisation(cv_structured, offre)
        formation_detail    = self._score_formation(cv_structured, offre)

        scores_numeriques = {
            "sbert":        self._score_sbert(cv_embedding, offre_embedding),
            "competences":  competences_detail["score"],
            "experience":   experience_detail["score"],
            "localisation": localisation_detail["score"],
            "formation":    formation_detail["score"]
        }

        score_final = sum(scores_numeriques[k] * POIDS[k] for k in scores_numeriques)

        return {
            "score_final": round(score_final, 3),
            "detail": {
                "sbert":        round(scores_numeriques["sbert"], 3),
                "competences":  competences_detail,
                "experience":   experience_detail,
                "localisation": localisation_detail,
                "formation":    formation_detail
            }
        }

    def _score_sbert(self, cv_embedding, offre_embedding) -> float:
        """Similarité cosinus entre le CV et l'offre."""
        return float(cosine_similarity(cv_embedding, offre_embedding)[0][0])

    def _score_competences(self, cv_structured: dict, offre: dict) -> dict:
        """
        Calcule le taux de compétences du CV présentes dans l'offre.
        Retourne le score, les listes de compétences CV/offre, matchées et manquantes.
        """
        texte_offre = build_offer_text(offre).lower()
        competences_offre_set = set(
            c for c in COMPETENCES_CONNUES if c.lower() in texte_offre
        )
        competences_cv = set(cv_structured["competences"])

        if not competences_offre_set:
            return {
                "score":      0.0,
                "cv":         sorted(competences_cv),
                "offre":      [],
                "match":      [],
                "manquantes": []
            }

        # Match normalisé — "Power BI" == "PowerBI"
        match = sorted([
            c for c in competences_cv
            if any(_normalize(c) == _normalize(o) for o in competences_offre_set)
        ])
        manquantes = sorted([
            c for c in competences_offre_set
            if not any(_normalize(c) == _normalize(cv) for cv in competences_cv)
        ])
        score = len(match) / len(competences_offre_set) if competences_offre_set else 0.0

        return {
            "score":      round(score, 3),
            "cv":         sorted(competences_cv),
            "offre":      sorted(competences_offre_set),
            "match":      match,
            "manquantes": manquantes
        }

    def _score_experience(self, cv_structured: dict, offre: dict) -> dict:
        """
        Compare les années d'expérience du CV et de l'offre.
        Retourne le score, les années CV/offre, matchées et manquantes.
        """
        annees_cv = cv_structured.get("annees_experience", 0)
        label     = offre.get("experience_label", "") or ""
        match     = re.search(r'(\d+)', label)

        if not match:
            return {
                "score":      1.0,
                "cv":         annees_cv,
                "offre":      None,
                "match":      None,
                "manquantes": None
            }

        annees_requises  = int(match.group(1))
        annees_match     = min(annees_cv, annees_requises)
        annees_manquantes = max(0, annees_requises - annees_cv)

        if annees_cv >= annees_requises:
            score = 1.0
        elif annees_cv >= annees_requises - 1:
            score = 0.5
        else:
            score = 0.0

        return {
            "score":      score,
            "cv":         annees_cv,
            "offre":      annees_requises,
            "match":      annees_match,
            "manquantes": annees_manquantes
        }

    def _score_localisation(self, cv_structured: dict, offre: dict) -> dict:
        """
        Compare la localisation du CV et de l'offre.
        Calcule la distance en km si les coordonnées GPS sont disponibles.
        """
        loc_cv    = (cv_structured.get("localisation") or "").lower()
        workplace = offre.get("workplace_label") or ""
        postal    = (offre.get("workplace_postal_code") or "")[:2]
        lat_offre = offre.get("workplace_latitude")
        lon_offre = offre.get("workplace_longitude")

        if not loc_cv or loc_cv == "non précisé":
            score = 0.5
        elif re.search(r'\b' + re.escape(loc_cv) + r'\b', workplace.lower()) \
                or loc_cv[:2] == postal:
            score = 1.0
        else:
            score = 0.0

        coords_cv  = COORDS_VILLES.get(cv_structured.get("localisation", ""))
        distance_km = None
        if coords_cv and lat_offre and lon_offre:
            distance_km = _haversine(coords_cv[0], coords_cv[1], lat_offre, lon_offre)

        return {
            "score":       round(score, 3),
            "cv":          cv_structured.get("localisation") or "Non précisé",
            "offre":       workplace or "Non précisé",
            "distance_km": distance_km
        }

    def _score_formation(self, cv_structured: dict, offre: dict) -> dict:
        """
        Compare le niveau de formation du CV et celui requis par l'offre.
        Retourne le score et le détail CV/offre.
        """
        formation_cv      = cv_structured.get("formation", "Non précisé")
        niveau_cv         = FORMATION_SCORE.get(formation_cv, 0)
        formation_requise = offre.get("formation_requise") or ""
        # Normalise "Bac +4" → "Bac+4", "bac + 5" → "Bac+5"
        formation_requise_normalized = re.sub(r'Bac\s*\+', 'Bac+', formation_requise, flags=re.IGNORECASE)

        # Données absentes → pas de pénalité
        if not formation_requise:
            return {
                "score": 1.0,
                "cv":    formation_cv,
                "offre": "Non précisé"
            }

        # Cherche le niveau requis dans le texte (du plus élevé au plus bas)
        niveau_requis = 0
        for formation, niveau in sorted(
            FORMATION_SCORE.items(), key=lambda x: x[1], reverse=True
        ):
            if formation.lower() in formation_requise_normalized.lower():
                niveau_requis = niveau
                break

        # Niveau non reconnu → pas de pénalité
        if niveau_requis == 0:
            return {
                "score": 1.0,
                "cv":    formation_cv,
                "offre": formation_requise
            }

        if niveau_cv >= niveau_requis:
            score = 1.0
        elif niveau_cv >= niveau_requis - 1:
            score = 0.5
        else:
            score = 0.0

        return {
            "score": score,
            "cv":    formation_cv,
            "offre": formation_requise
        }
