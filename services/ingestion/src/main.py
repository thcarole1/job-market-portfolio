import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.ingestion.src.collectors.france_travail import FranceTravailCollector
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ingestion.src.utils.normalizer import normalize_france_travail
from services.ml.src.encoder import encode_offer, MODEL_NAME

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


def _get_existing_ids(mongo_loader) -> set:
    """Retourne l'ensemble des IDs déjà présents dans offres_normalisees."""
    col = mongo_loader.db["offres_normalisees"]
    ids = {doc["id"] for doc in col.find({}, projection={"id": 1, "_id": 0})}
    logger.info(f"{len(ids)} IDs existants chargés depuis MongoDB")
    return ids


def _get_min_creation_date(mongo_loader) -> str | None:
    """
    Retourne la date de création de l'offre la plus récente en base,
    moins 1 jour de marge, au format ISO 8601.
    Retourne None si la base est vide (collecte complète).
    """
    col = mongo_loader.db["offres_normalisees"]
    doc = col.find_one(
        {"creation_date": {"$exists": True}},
        sort=[("creation_date", -1)],
        projection={"creation_date": 1}
    )

    if not doc:
        logger.info("Base vide — collecte complète sans filtre date")
        return None

    last_date = doc["creation_date"]
    try:
        dt = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
        dt = dt - timedelta(days=1)
        result = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        logger.info(f"Dernière offre en base : {last_date} → filtre depuis : {result}")
        return result
    except (ValueError, AttributeError):
        logger.warning(f"Format date non reconnu : {last_date} — collecte complète")
        return None


def run_ingestion() -> None:
    """
    Étapes 1 à 5 du pipeline :
    collecte → insertion brutes → normalisation → embedding → indexation ES.
    Appelable par Airflow (t1 + t2) ou directement.
    """
    # 1. Connexion MongoDB
    mongo_loader = Mongoloader()

    # 2. Filtres incrémantaux
    existing_ids      = _get_existing_ids(mongo_loader)
    min_creation_date = _get_min_creation_date(mongo_loader)

    # 3. Collecte France Travail
    collector     = FranceTravailCollector()
    offres_brutes = collector.collect_all_offers(
        rome_codes=ROME_CODES,
        existing_ids=existing_ids,
        min_creation_date=min_creation_date,
    )
    logger.info(f"{len(offres_brutes)} nouvelles offres à traiter")

    if not offres_brutes:
        logger.info("Aucune nouvelle offre — pipeline terminé.")
        return

    # 4. Insertion brutes dans MongoDB
    logger.info("Insertion des offres brutes dans MongoDB...")
    for offre in offres_brutes:
        mongo_loader.insert_raw_offer(offer=offre)

    # 5. Normalisation + encoding SBERT + insertion normalisées + indexation ES
    elastic_loader = Elasticloader()
    logger.info("Normalisation, encoding SBERT et indexation des offres...")
    for offre in offres_brutes:
        offre_normalisee = normalize_france_travail(offre)
        offre_normalisee["embedding"]       = encode_offer(offre_normalisee)
        offre_normalisee["embedding_model"] = MODEL_NAME
        mongo_loader.insert_normalized_offer(offer=offre_normalisee)
        elastic_loader.index_offer(offer=offre_normalisee)

    logger.info("Pipeline d'ingestion terminé ✅")


def run_enrich() -> None:
    """
    Étape 6 : enrichissement SBERT zero-shot des nouvelles offres.
    Appelable par Airflow (t3) ou directement.
    """
    logger.info("Enrichissement skills (SBERT zero-shot) des nouvelles offres...")
    try:
        from scripts.enrich_skills import run as enrich_skills_run
        enrich_skills_run(
            force=False,
            threshold=0.75,
            dry_run=False,
            batch_size=50,
        )
        logger.info("Enrichissement skills terminé ✅")
    except Exception as e:
        logger.error(f"Enrichissement skills échoué : {e}")
        raise  # re-lève pour qu'Airflow marque la tâche en échec


if __name__ == "__main__":
    run_ingestion()
    run_enrich()
