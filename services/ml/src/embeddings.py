import numpy as np
import pickle
import logging
from sentence_transformers import SentenceTransformer
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.features import build_offer_text

logger = logging.getLogger(__name__)

from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT / "services/ml/models"
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

def train_sbert():
    """
    Encode toutes les offres normalisées avec SBERT.
    Sauvegarde les embeddings, les ids et le nom du modèle dans models/.
    """
    logger.info("Chargement du modèle SBERT...")
    model = SentenceTransformer(MODEL_NAME)

    logger.info("Connexion à MongoDB...")
    loader = Mongoloader()
    offres = list(loader.db["offres_normalisees"].find({}, {"_id": 0}))
    logger.info(f"Nombre d'offres récupérées : {len(offres)}")

    logger.info("Construction des textes d'offres...")
    ids = [o["id"] for o in offres]
    texts = [build_offer_text(o) for o in offres]

    logger.info("Encodage SBERT en cours (peut prendre quelques minutes sur CPU)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    logger.info("Sauvegarde des embeddings...")
    np.save(f"{MODELS_DIR}/sbert_embeddings.npy", embeddings)

    with open(f"{MODELS_DIR}/sbert_ids.pkl", "wb") as f:
        pickle.dump(ids, f)

    logger.info(f"SBERT entraîné — {len(ids)} offres encodées, shape: {embeddings.shape}")
    return embeddings, ids
