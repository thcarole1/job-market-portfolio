from elasticsearch import Elasticsearch, ApiError
import logging
logger = logging.getLogger(__name__)

from config.settings import settings

class Elasticloader:
    def __init__(self):
        '''connexion à ElasticSearch '''
        logger.info("Instanciation de ElasticSearch - Tentative de connexion à ElasticSearch")
        try:
            self.es = Elasticsearch(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}")
            logger.info("Instanciation de ElasticSearch - Connexion à ElasticSearch réussie !")
        except ApiError as e:
            logger.error(f"Erreur connexion à ElasticSearch : {e}")
            raise

    def index_offer(self, offer: dict):
        '''Indexation d'une offre à ElasticSearch '''
        logger.info("Insertion d'une offre dans ElasticSearch")
        try:
            self.es.index(
                index=settings.ELASTICSEARCH_INDEX,
                id=offer["id"],    # utilise l'id de l'offre comme id ES → évite les doublons
                document=offer)
            logger.info("Indexation d'une offre dans ElasticSearch réussie !")
        except ApiError as e:
            logger.error(f"Erreur indexation à ElasticSearch : {e}")
            raise
