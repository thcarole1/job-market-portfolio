import logging
from sentence_transformers import SentenceTransformer
from services.ml.src.features import build_offer_text

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

# Chargement unique du modèle au niveau du module
# → évite de recharger le modèle à chaque appel
_model = None

def get_model() -> SentenceTransformer:
    """Charge le modèle SBERT une seule fois (singleton)."""
    global _model
    if _model is None:
        logger.info(f"Chargement du modèle SBERT : {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def encode_offer(offre: dict) -> list:
    """
    Encode une offre normalisée avec SBERT.
    Retourne l'embedding sous forme de liste (compatible JSON/ES).
    """
    model = get_model()
    text = build_offer_text(offre)
    embedding = model.encode(text)
    return embedding.tolist()
