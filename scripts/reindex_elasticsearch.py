import logging
import sys
sys.path.insert(0, ".")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader

def reindex_elasticsearch():
    """
    Réindexe toutes les offres depuis MongoDB vers Elasticsearch.
    Utile après un changement de mapping ES — pas besoin de recalculer les embeddings.
    """
    mongo_loader  = Mongoloader()
    elastic_loader = Elasticloader()

    offres = list(mongo_loader.db["offres_normalisees"].find({}, {"_id": 0}))
    logger.info(f"{len(offres)} offres à réindexer...")

    for i, offre in enumerate(offres):
        elastic_loader.index_offer(offre)
        if (i + 1) % 100 == 0:
            logger.info(f"{i + 1}/{len(offres)} offres réindexées...")

    logger.info("Réindexation terminée ✅")

if __name__ == "__main__":
    reindex_elasticsearch()
