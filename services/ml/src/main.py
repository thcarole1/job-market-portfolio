import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ml.src.train import train_tfidf
from services.ml.src.embeddings import train_sbert


if __name__ == "__main__":
    logger.info("Lancement entraînement modèle TF-IDF...")
    train_tfidf()
    logger.info("Fin entraînement modèle TF-IDF...")

    logger.info("Lancement entraînement SBERT...")
    train_sbert()
    logger.info("Fin entraînement SBERT...")
