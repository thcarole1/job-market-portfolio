from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.features import build_offer_text

from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT / "services/ml/models"

def train_tfidf(output_path: str = "services/ml/models") :
    #1. Récupère toutes les offres normalisées depuis MongoDB
    loader = Mongoloader()
    offres = list(loader.db["offres_normalisees"].find())

    logger.info(f"Nombre d'offres récupérées : {len(offres)}")

    #2. Construit le texte de chaque offre avec build_offer_text()
    corpus = [build_offer_text(offre) for offre in offres]
    ids    = [offre["id"] for offre in offres]

    #3. Entraîne un TfidfVectorizer sur ce corpus
    vectorizer = TfidfVectorizer()
    logger.info(f"Début de l'entraînement du tfidf vectorizer.")
    tfidf_matrix = vectorizer.fit_transform(corpus)  # corpus = liste de textes
    logger.info(f"Fin de l'entraînement du tfidf vectorizer.")

    #4. Sauvegarde le vectorizer et la matrice TF-IDF en .pkl
    MODELS_DIR.mkdir(parents=True, exist_ok=True)  # ← crée le dossier si absent

    with open(f"{MODELS_DIR}/tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    logger.info(f"Sauvegarde du vectorizer réussie.")

    with open(f"{MODELS_DIR}/tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)
    logger.info(f"Sauvegarde de la matrice tfidf réussie.")

    with open(f"{MODELS_DIR}/tfidf_ids.pkl", "wb") as f:
        pickle.dump(ids, f)
    logger.info(f"Sauvegarde des identifiants réussie.")
