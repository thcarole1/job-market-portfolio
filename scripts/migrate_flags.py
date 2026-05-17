"""
migrate_flags.py
----------------
Script de migration one-shot — ajoute les champs de tracking
_normalized et _es_indexed aux offres existantes en base.

Sans ce script, toutes les offres existantes seraient retraitées
par le nouveau pipeline granulaire.

Usage :
    PYTHONPATH=. python scripts/migrate_flags.py
    PYTHONPATH=. python scripts/migrate_flags.py --dry-run
"""

import argparse
import logging
from pymongo import UpdateMany

from services.ingestion.src.loaders.mongo_loader import Mongoloader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_flags")


def run(dry_run: bool = False) -> None:
    """
    Migration :
    - offres_brutes    : _normalized=True  (toutes les offres existantes sont déjà normalisées)
    - offres_normalisees : _es_indexed=True (toutes les offres existantes sont déjà indexées dans ES)
    """
    loader = Mongoloader()

    # ── offres_brutes : marquer comme normalisées ─────────────────────────────
    col_brutes = loader.db["offres_brutes"]
    n_brutes   = col_brutes.count_documents({"_normalized": {"$exists": False}})
    logger.info(f"offres_brutes sans _normalized : {n_brutes}")

    if not dry_run and n_brutes > 0:
        result = col_brutes.update_many(
            {"_normalized": {"$exists": False}},
            {"$set": {"_normalized": True}}
        )
        logger.info(f"offres_brutes mises à jour : {result.modified_count}")
    elif dry_run:
        logger.info(f"[DRY-RUN] {n_brutes} offres_brutes seraient mises à jour")

    # ── offres_normalisees : marquer comme indexées ES ────────────────────────
    col_norm = loader.db["offres_normalisees"]
    n_norm   = col_norm.count_documents({"_es_indexed": {"$exists": False}})
    logger.info(f"offres_normalisees sans _es_indexed : {n_norm}")

    if not dry_run and n_norm > 0:
        result = col_norm.update_many(
            {"_es_indexed": {"$exists": False}},
            {"$set": {"_es_indexed": True}}
        )
        logger.info(f"offres_normalisees mises à jour : {result.modified_count}")
    elif dry_run:
        logger.info(f"[DRY-RUN] {n_norm} offres_normalisees seraient mises à jour")

    # ── offres_normalisees sans embedding : marquer _es_indexed=False ─────────
    # (ces offres devront être retraitées par run_embeddings + run_indexation_es)
    n_no_embed = col_norm.count_documents(
        {"embedding": None, "_es_indexed": {"$exists": False}}
    )
    if n_no_embed > 0:
        logger.warning(f"{n_no_embed} offres sans embedding détectées — seront retraitées")

    logger.info("Migration terminée ✅" if not dry_run else "[DRY-RUN] Migration simulée ✅")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migration flags _normalized et _es_indexed")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans écrire")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
