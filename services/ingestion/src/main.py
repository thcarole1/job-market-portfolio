import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.collectors.france_travail import FranceTravailCollector
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ingestion.src.utils.normalizer import normalize_france_travail
from services.ml.src.encoder import encode_offer, MODEL_NAME

if __name__ == "__main__":

    # 1. Collecte France Travail
    collector = FranceTravailCollector()

    ROME_CODES = [
    "M1811",  # Data Engineer — suffisant pour tester
    "M1405",  # Data Scientist
    ]

    offres_brutes = collector.collect_all_offers(rome_codes=ROME_CODES)
    logger.info(f"{len(offres_brutes)} offres collectées")

    # 2. Insertion brutes dans MongoDB
    mongo_loader = Mongoloader()
    logger.info("Insertion des offres brutes dans MongoDB...")
    for offre in offres_brutes:
        mongo_loader.insert_raw_offer(offer=offre)

    # 3. Normalisation
    # 4. Encoding SBERT
    # 5. Insertion normalisées dans MongoDB
    # 6. Indexation Elasticsearch
    elastic_loader = Elasticloader()
    logger.info("Normalisation, encoding SBERT et indexation des offres...")

    for offre in offres_brutes:
        offre_normalisee = normalize_france_travail(offre)

        # Calcul de l'embedding SBERT
        offre_normalisee["embedding"]       = encode_offer(offre_normalisee)
        offre_normalisee["embedding_model"] = MODEL_NAME

        mongo_loader.insert_normalized_offer(offer=offre_normalisee)
        elastic_loader.index_offer(offer=offre_normalisee)

    logger.info("Pipeline d'ingestion terminé ✅")
