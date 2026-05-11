import logging
import requests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from config.settings import settings

def reset_mongodb():
    """Vide les collections MongoDB."""
    loader = Mongoloader()
    loader.db["offres_brutes"].drop()
    loader.db["offres_normalisees"].drop()
    logger.info("MongoDB vidé ✅")

def reset_elasticsearch():
    """Supprime l'index Elasticsearch."""
    url = f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}/{settings.ELASTICSEARCH_INDEX}"
    response = requests.delete(url)
    if response.status_code == 200:
        logger.info("Elasticsearch vidé ✅")
    elif response.status_code == 404:
        logger.info("Index ES inexistant — rien à supprimer ✅")
    else:
        logger.error(f"Erreur ES : {response.status_code} — {response.text}")

if __name__ == "__main__":
    reset_mongodb()
    reset_elasticsearch()
    logger.info("Reset complet ✅")


'''
PYTHONPATH=. python scripts/reset_db.py
docker compose down -v
docker compose build
docker compose up -d
'''
