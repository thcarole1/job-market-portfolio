import re
import logging
from sklearn.metrics.pairwise import cosine_similarity
from services.ml.src.features import build_offer_text

logger = logging.getLogger(__name__)

# ── Pondérations ──────────────────────────────────────
POIDS = {
    "sbert":        0.40,
    "competences":  0.30,
    "experience":   0.15,
    "localisation": 0.10,
    "formation":    0.05
}

# ── Mapping formation → niveau numérique ─────────────
FORMATION_SCORE = {
    "Bac": 1, "Bac+2": 2, "Bac+3": 3, "Licence": 3,
    "Bachelor": 3, "Bac+5": 5, "Master": 5,
    "Ingénieur": 5, "Doctorat": 6, "PhD": 6,
    "Non précisé": 0
}

COMPETENCES_CONNUES = [
    "Python", "SQL", "Scala", "Java", "R",
    "Spark", "PySpark", "Kafka", "Hadoop", "Airflow",
    "MongoDB", "PostgreSQL", "Elasticsearch", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes",
    "dbt", "Snowflake", "Databricks", "Tableau",
    "Power BI", "Grafana", "Kibana", "FastAPI",
    "Git", "CI/CD", "Terraform", "MLflow",
    "pandas", "numpy", "scikit-learn", "TensorFlow",
    "PyTorch", "HuggingFace", "LangChain"
]

class HybridScorer:

    def score(self, cv_structured: dict, cv_embedding,
              offre: dict, offre_embedding) -> dict:
        """
        Calcule le score hybride entre un CV et une offre.
        Retourne un dict avec score_final et détail par critère.
        """
        scores = {
            "sbert":        self._score_sbert(cv_embedding, offre_embedding),
            "competences":  self._score_competences(cv_structured, offre),
            "experience":   self._score_experience(cv_structured, offre),
            "localisation": self._score_localisation(cv_structured, offre),
            "formation":    self._score_formation(cv_structured, offre)
        }
        score_final = sum(scores[k] * POIDS[k] for k in scores)
        return {
            "score_final": round(score_final, 3),
            "detail": {k: round(v, 3) for k, v in scores.items()}
        }

    def _score_sbert(self, cv_embedding, offre_embedding) -> float:
        """Similarité cosinus entre CV et offre."""
        return float(cosine_similarity(cv_embedding, offre_embedding)[0][0])

    def _score_competences(self, cv_structured: dict, offre: dict) -> float:
        """% de compétences du CV présentes dans l'offre."""
        texte_offre = build_offer_text(offre).lower()
        competences_offre = [c for c in COMPETENCES_CONNUES if c.lower() in texte_offre]
        competences_cv = set(cv_structured["competences"])
        if not competences_offre:
            return 0.0
        return len(competences_cv & set(competences_offre)) / len(set(competences_offre))

    def _score_experience(self, cv_structured: dict, offre: dict) -> float:
        """1.0 si expérience compatible, 0.5 si proche, 0.0 sinon."""
        annees_cv = cv_structured.get("annees_experience", 0)
        label = offre.get("experience_label", "") or ""
        match = re.search(r'(\d+)', label)
        if not match:
            return 1.0
        annees_requises = int(match.group(1))
        if annees_cv >= annees_requises:
            return 1.0
        elif annees_cv >= annees_requises - 1:
            return 0.5
        else:
            return 0.0

    def _score_localisation(self, cv_structured: dict, offre: dict) -> float:
        """1.0 si même ville/département, 0.0 sinon."""
        loc_cv = (cv_structured.get("localisation") or "").lower()
        workplace = (offre.get("workplace_label") or "").lower()
        postal = (offre.get("workplace_postal_code") or "")[:2]
        if not loc_cv or loc_cv == "non précisé":
            return 0.5
        if re.search(r'\b' + re.escape(loc_cv) + r'\b', workplace) or loc_cv[:2] == postal:
            return 1.0
        return 0.0

    def _score_formation(self, cv_structured: dict, offre: dict) -> float:
        """1.0 si formation suffisante, 0.5 si inférieure d'un niveau, 0.0 sinon."""
        formation_requise = offre.get("formation_requise")
        if not formation_requise:
            return 1.0
        niveau_cv = FORMATION_SCORE.get(cv_structured.get("formation", "Non précisé"), 0)
        match = re.search(r'Bac\+(\d+)', formation_requise, re.IGNORECASE)
        if match:
            niveau_requis = int(match.group(1))
        else:
            return 1.0
        if niveau_cv >= niveau_requis:
            return 1.0
        elif niveau_cv >= niveau_requis - 1:
            return 0.5
        else:
            return 0.0
