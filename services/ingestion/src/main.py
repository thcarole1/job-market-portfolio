import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.collectors.france_travail import FranceTravailCollector
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ingestion.src.utils.normalizer import normalize_france_travail

if __name__ == "__main__":
    #1. Collecte France Travail
    collector = FranceTravailCollector()
    offres_brutes = collector.collect_all_offers(mots_cles="data engineer")
    logger.info(f"{len(offres_brutes)} offres collectées")

    #2. Insertion brutes dans MongoDB
    mongo_loader = Mongoloader()
    logger.info(f"Insertion des offres brutes dans MongoDB...")
    for offre in offres_brutes:
        mongo_loader.insert_raw_offer(offer=offre)

    #3. Normalisation + #4. Insertion normalisées dans MongoDB + #5. Indexation Elasticsearch
    elastic_loader = Elasticloader()
    logger.info(f"Normalisation des offres brutes, Insertion des offres normalisées dans MongoDB et Indexation des offres normalisées dasn ElasticSearch...")
    for offre in offres_brutes:
        offre_normalisee = normalize_france_travail(offre)
        mongo_loader.insert_normalized_offer(offer=offre_normalisee)
        elastic_loader.index_offer(offer=offre_normalisee)
