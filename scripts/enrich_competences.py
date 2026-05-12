import re
import logging
import sys
sys.path.insert(0, ".")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.constants import COMPETENCES_CONNUES
from services.ml.src.features import build_offer_text

def _extract_competences_offre(offre: dict) -> list:
    """Extrait les compétences connues depuis le texte de l'offre."""
    texte = build_offer_text(offre).lower()
    return [
        c for c in COMPETENCES_CONNUES
        if re.search(r'\b' + re.escape(c.lower()) + r'\b', texte)
    ]

def enrich_competences():
    loader = Mongoloader()
    total  = loader.db["offres_normalisees"].count_documents({})
    logger.info(f"{total} offres à enrichir...")

    # Une seule requête — itère sur le curseur sans tout charger en RAM
    curseur = loader.db["offres_normalisees"].find({}, {"_id": 1, "title": 1, "description": 1, "name_label": 1, "competences": 1, "languages": 1, "professional_qualities": 1})

    for i, offre in enumerate(curseur):
        mongo_id   = offre.pop("_id")  # ← extrait _id avant d'analyser
        competences = _extract_competences_offre(offre)

        loader.db["offres_normalisees"].update_one(
            {"_id": mongo_id},
            {"$set": {"competences_detectees": competences}}
        )
        if (i + 1) % 500 == 0:
            logger.info(f"{i + 1}/{total} offres enrichies...")

    logger.info("Enrichissement terminé ✅")

if __name__ == "__main__":
    enrich_competences()
