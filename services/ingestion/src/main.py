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
        # ── Data & IA ─────────────────────────────────────
        "M1811",  # Data Engineer
        "M1405",  # Data Scientist
        "M1403",  # Études statistiques
        "M1804",  # Études et développement de systèmes d'information
        "M1805",  # Études et développement informatique
        "M1810",  # Production et exploitation de systèmes d'information

        # ── Informatique & SI ─────────────────────────────
        "M1802",  # Expertise et support en systèmes d'information
        "M1803",  # Direction des systèmes d'information
        "M1806",  # Conseil et maîtrise d'ouvrage en SI
        "M1807",  # Architecture et intégration informatique
        "M1808",  # Exploitation de systèmes de communication
        "M1809",  # Organisation des systèmes d'information

        # ── Management & conseil ──────────────────────────
        "M1402",  # Conseil en organisation et management
        "M1404",  # Management et ingénierie études R&D
        "M1205",  # Direction administrative et financière
        "M1206",  # Management de projet

        # ── Finance & comptabilité ────────────────────────
        "M1202",  # Audit et contrôle comptables
        "M1203",  # Comptabilité
        "M1204",  # Finance et trésorerie
        "M1207",  # Tenue de comptabilité

        # ── Marketing & commercial ────────────────────────
        "M1705",  # Marketing
        "D1401",  # Commerce de détail
        "D1402",  # Relation technico-commerciale
        "D1403",  # Management en force de vente

        # ── RH & formation ────────────────────────────────
        "M1501",  # Assistanat en ressources humaines
        "M1502",  # Développement des ressources humaines
        "M1503",  # Management des ressources humaines

        # ── Santé & social ────────────────────────────────
        "K2204",  # Aide soignant
        "K2102",  # Infirmier
        "K1401",  # Travail social
        "K2301",  # Médecin

        # ── BTP & industrie ───────────────────────────────
        "F1703",  # Maçonnerie
        "H2902",  # Ingénierie en industrie
        "H2503",  # Électromécanique

        # ── Distribution & logistique ─────────────────────
        "D1507",  # Mise en rayon
        "N1301",  # Logistique
        "N1303",  # Transport de marchandises

        # ── Restauration & hôtellerie ─────────────────────
        "G1703",  # Restauration
        "G1601",  # Hôtellerie
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

    # 7. Enrichissement skills — uniquement les nouvelles offres
    #    (filtre automatique via $exists: False dans enrich_skills.run())
    logger.info("Enrichissement skills (SBERT zero-shot) des nouvelles offres...")
    try:
        from scripts.enrich_skills import run as enrich_skills_run
        enrich_skills_run(
            force=False,       # uniquement les offres sans skills_extraits
            threshold=0.75,
            dry_run=False,
            batch_size=50,
        )
        logger.info("Enrichissement skills terminé ✅")
    except Exception as e:
        # L'enrichissement ne doit jamais bloquer la collecte
        logger.error(f"Enrichissement skills échoué — pipeline non bloqué : {e}")
