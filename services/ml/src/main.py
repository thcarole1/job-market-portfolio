import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ml.src.train import train_tfidf

if __name__ == "__main__":
    logger.info(f"Lancement entraînement modèle TF-IDF...")
    train_tfidf(output_path = "services/ml/models")
    logger.info(f"Fin entraînement modèle TF-IDF...")
