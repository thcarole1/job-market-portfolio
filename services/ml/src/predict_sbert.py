import numpy as np
import pickle
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
MODELS_DIR = "services/ml/models"

def recommend_offers_sbert(cv_text: str, top_n: int = 10, offer_ids: list = None) -> list:
    """
    Recommande les offres les plus similaires au texte du CV
    en utilisant les embeddings SBERT et la similarité cosinus.
    Retourne une liste de dicts {id, score} triés par score décroissant.
    """
    logger.info("Chargement du modèle SBERT...")
    model = SentenceTransformer(MODEL_NAME)

    logger.info("Chargement des embeddings et ids...")
    embeddings = np.load(f"{MODELS_DIR}/sbert_embeddings.npy")
    with open(f"{MODELS_DIR}/sbert_ids.pkl", "rb") as f:
        ids = pickle.load(f)

    # Filtrage par ids si fourni
    if offer_ids is not None:
        indices = [i for i, id_ in enumerate(ids) if id_ in set(offer_ids)]
        embeddings = embeddings[indices]
        ids = [ids[i] for i in indices]
        logger.info(f"Filtrage : {len(ids)} offres retenues")

    logger.info("Encodage du CV...")
    cv_embedding = model.encode([cv_text])

    logger.info("Calcul des scores de similarité...")
    scores = cosine_similarity(cv_embedding, embeddings)[0]

    logger.info(f"Récupération des {top_n} offres les plus similaires.")
    top_indices = np.argsort(scores)[::-1][:top_n]

    return [{"id": ids[i], "score": float(scores[i])} for i in top_indices]
