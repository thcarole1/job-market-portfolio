from elasticsearch import Elasticsearch, ApiError
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from config.settings import settings

MAPPING_PATH = Path(__file__).resolve().parents[4] / "storage/elasticsearch/mappings.json"

class Elasticloader:
    def __init__(self):
        '''Connexion à ElasticSearch et création de l'index si nécessaire.'''
        logger.info("Instanciation de ElasticSearch - Tentative de connexion à ElasticSearch")
        try:
            self.es = Elasticsearch(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}")
            self.index_name = settings.ELASTICSEARCH_INDEX
            with open(MAPPING_PATH) as f:
                self.mapping = json.load(f)
            self._create_index_if_not_exists()
            logger.info("Instanciation de ElasticSearch - Connexion à ElasticSearch réussie !")
        except ApiError as e:
            logger.error(f"Erreur connexion à ElasticSearch : {e}")
            raise

    def _create_index_if_not_exists(self):
        """Crée l'index ES avec le bon mapping si il n'existe pas encore."""
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=self.mapping)
            logger.info(f"Index '{self.index_name}' créé avec mapping depuis fichier.")
        else:
            logger.info(f"Index '{self.index_name}' existe déjà.")

    def index_offer(self, offer: dict):
        '''Indexation d'une offre dans ElasticSearch.'''
        logger.info("Insertion d'une offre dans ElasticSearch")
        try:
            self.es.index(
                index=self.index_name,
                id=offer["id"],
                document=offer
            )
            logger.info("Indexation d'une offre dans ElasticSearch réussie !")
        except ApiError as e:
            logger.error(f"Erreur indexation à ElasticSearch : {e}")
            raise

    def delete_index(self):
        """Supprime l'index ES — utile pour réindexer proprement."""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            logger.info(f"Index '{self.index_name}' supprimé.")
