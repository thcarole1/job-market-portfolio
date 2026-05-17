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


# ── Helpers ───────────────────────────────────────────────────────────────────

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


# ── Tâche 1 : Collecte + insertion brutes ────────────────────────────────────

def run_collecte() -> None:
    """
    Tâche 1 — Collecte France Travail + insertion dans offres_brutes.
    - Filtre incrémental par date et IDs existants
    - Insère uniquement les nouvelles offres (upsert)
    - Marque les offres brutes comme non normalisées (normalized=False)
    """
    mongo_loader = Mongoloader()
    existing_ids      = _get_existing_ids(mongo_loader)
    min_creation_date = _get_min_creation_date(mongo_loader)

    collector     = FranceTravailCollector()
    offres_brutes = collector.collect_all_offers(
        rome_codes=ROME_CODES,
        existing_ids=existing_ids,
        min_creation_date=min_creation_date,
    )
    logger.info(f"{len(offres_brutes)} nouvelles offres collectées")

    if not offres_brutes:
        logger.info("Aucune nouvelle offre — tâche terminée.")
        return

    logger.info("Insertion des offres brutes dans MongoDB...")
    for offre in offres_brutes:
        # Marquer comme non normalisée pour la tâche suivante
        offre["_normalized"] = False
        mongo_loader.insert_raw_offer(offer=offre)

    logger.info(f"Tâche 1 terminée — {len(offres_brutes)} offres brutes insérées ✅")


# ── Tâche 2 : Normalisation + insertion normalisées ───────────────────────────

def run_normalisation() -> None:
    """
    Tâche 2 — Normalisation des offres brutes + insertion dans offres_normalisees.
    - Lit les offres brutes non encore normalisées (_normalized=False)
    - Normalise et insère dans offres_normalisees (sans embedding)
    - Marque les offres brutes comme normalisées (_normalized=True)
    """
    mongo_loader = Mongoloader()
    col_brutes = mongo_loader.db["offres_brutes"]

    # Lire uniquement les offres non encore normalisées
    offres_a_normaliser = list(col_brutes.find({"_normalized": False}))
    logger.info(f"{len(offres_a_normaliser)} offres brutes à normaliser")

    if not offres_a_normaliser:
        logger.info("Aucune offre à normaliser — tâche terminée.")
        return

    for offre in offres_a_normaliser:
        offre_normalisee = normalize_france_travail(offre)
        # Pas d'embedding encore — sera calculé à la tâche suivante
        offre_normalisee["embedding"] = None
        offre_normalisee["embedding_model"] = None
        mongo_loader.insert_normalized_offer(offer=offre_normalisee)
        # Marquer l'offre brute comme normalisée
        col_brutes.update_one(
            {"id": offre["id"]},
            {"$set": {"_normalized": True}}
        )

    logger.info(f"Tâche 2 terminée — {len(offres_a_normaliser)} offres normalisées ✅")


# ── Tâche 3 : Calcul des embeddings SBERT ────────────────────────────────────

def run_embeddings() -> None:
    """
    Tâche 3 — Calcul des embeddings SBERT pour les offres normalisées.
    - Lit les offres normalisées sans embedding (embedding=None)
    - Calcule l'embedding SBERT (768 dimensions)
    - Met à jour MongoDB
    """
    mongo_loader = Mongoloader()
    col = mongo_loader.db["offres_normalisees"]

    offres_sans_embedding = list(col.find(
        {"embedding": None},
        projection={"_id": 1, "id": 1, "title": 1, "description": 1,
                    "rome_label": 1, "competences_detectees": 1}
    ))
    logger.info(f"{len(offres_sans_embedding)} offres à encoder")

    if not offres_sans_embedding:
        logger.info("Aucune offre à encoder — tâche terminée.")
        return

    for offre in offres_sans_embedding:
        embedding = encode_offer(offre)
        col.update_one(
            {"id": offre["id"]},
            {"$set": {
                "embedding":       embedding,
                "embedding_model": MODEL_NAME,
            }}
        )

    logger.info(f"Tâche 3 terminée — {len(offres_sans_embedding)} embeddings calculés ✅")


# ── Tâche 4 : Indexation Elasticsearch ───────────────────────────────────────

def run_indexation_es() -> None:
    """
    Tâche 4 — Indexation des offres normalisées dans Elasticsearch.
    - Lit les offres normalisées avec embedding mais non encore indexées
    - Indexe dans Elasticsearch (dense_vector KNN)
    """
    mongo_loader   = Mongoloader()
    elastic_loader = Elasticloader()
    col = mongo_loader.db["offres_normalisees"]

    # Lire les offres avec embedding non encore indexées dans ES
    offres_a_indexer = list(col.find(
        {"embedding": {"$ne": None}, "_es_indexed": {"$ne": True}}
    ))
    logger.info(f"{len(offres_a_indexer)} offres à indexer dans Elasticsearch")

    if not offres_a_indexer:
        logger.info("Aucune offre à indexer — tâche terminée.")
        return

    for offre in offres_a_indexer:
        elastic_loader.index_offer(offer=offre)
        # Marquer comme indexée
        col.update_one(
            {"id": offre["id"]},
            {"$set": {"_es_indexed": True}}
        )

    logger.info(f"Tâche 4 terminée — {len(offres_a_indexer)} offres indexées dans ES ✅")


# ── Tâche 5 : Enrichissement skills ──────────────────────────────────────────

def run_enrich() -> None:
    """
    Tâche 5 — Enrichissement SBERT zero-shot des nouvelles offres.
    Extraction hard skills + soft skills (explicites + implicites).
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
        logger.info("Tâche 5 terminée — Enrichissement skills ✅")
    except Exception as e:
        logger.error(f"Enrichissement skills échoué : {e}")
        raise


# ── Point d'entrée local ──────────────────────────────────────────────────────

if __name__ == "__main__":
    run_collecte()
    run_normalisation()
    run_embeddings()
    run_indexation_es()
    run_enrich()
