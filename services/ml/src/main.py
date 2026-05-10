import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ml.src.train import train_tfidf

if __name__ == "__main__":
    logger.info("Lancement entraînement modèle TF-IDF...")
    train_tfidf()
    logger.info("Fin entraînement modèle TF-IDF...")

    # SBERT batch supprimé — embeddings calculés et stockés dans ES lors de la collecte
    logger.info("Pipeline ML terminé ✅")
