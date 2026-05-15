"""
enrich_skills.py
----------------
Script batch nocturne — enrichissement des offres avec skills_extraits.

Traite uniquement les offres qui n'ont pas encore le champ `skills_extraits`
(ou toutes si --force est passé), ce qui permet de le lancer chaque nuit
après la collecte France Travail sans re-traiter le corpus entier.

Usage :
    PYTHONPATH=. python scripts/enrich_skills.py
    PYTHONPATH=. python scripts/enrich_skills.py --force       # recalcule tout
    PYTHONPATH=. python scripts/enrich_skills.py --limit 100   # test sur N offres
    PYTHONPATH=. python scripts/enrich_skills.py --threshold 0.70
    PYTHONPATH=. python scripts/enrich_skills.py --dry-run     # sans écriture MongoDB
"""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone

from pymongo import UpdateOne

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.skills_extractor import SkillsExtractor

# ---------------------------------------------------------------------------
# Config logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("enrich_skills")


# ---------------------------------------------------------------------------
# Pipeline d'enrichissement
# ---------------------------------------------------------------------------

def run(
    force: bool = False,
    limit: int | None = None,
    threshold: float = 0.75,
    dry_run: bool = False,
    batch_size: int = 50,
) -> None:
    """
    Parcourt les offres MongoDB et enrichit chaque document avec `skills_extraits`.

    Paramètres
    ----------
    force : bool
        Si True, re-traite toutes les offres même si elles ont déjà `skills_extraits`.
    limit : int | None
        Nombre maximal d'offres à traiter (utile pour les tests).
    threshold : float
        Seuil de similarité cosine.
    dry_run : bool
        Si True, calcule mais n'écrit pas en MongoDB.
    batch_size : int
        Taille des batches MongoDB pour les bulk_write.
    """

    # -- Initialisation du modèle (une seule fois) ---------------------------
    logger.info("Initialisation du SkillsExtractor...")
    t0 = time.time()
    extractor = SkillsExtractor.get_instance(threshold=threshold)
    extractor.initialize()
    logger.info(f"Modèle prêt en {time.time() - t0:.1f}s")

    # -- Connexion MongoDB via MongoLoader -----------------------------------
    loader = Mongoloader()
    collection = loader.db["offres_normalisees"]

    # -- Requête MongoDB -----------------------------------------------------
    query: dict = {}
    if not force:
        query = {"skills_extraits": {"$exists": False}}

    cursor = collection.find(
        query,
        projection={"_id": 1, "title": 1, "description": 1},
        batch_size=batch_size,
    )
    if limit:
        cursor = cursor.limit(limit)

    # -- Traitement ----------------------------------------------------------
    total = collection.count_documents(query)
    if limit:
        total = min(total, limit)

    logger.info(
        f"{'[DRY-RUN] ' if dry_run else ''}"
        f"Traitement de {total} offres (seuil={threshold}, force={force})..."
    )

    bulk_ops: list[UpdateOne] = []
    n_ok = 0
    n_err = 0
    t_start = time.time()

    for i, doc in enumerate(cursor, start=1):
        try:
            description = doc.get("description") or ""
            title = doc.get("title") or ""

            result = extractor.extract(description=description, title=title)
            result["enriched_at"] = datetime.now(timezone.utc).isoformat()

            bulk_ops.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": {"skills_extraits": result}},
                )
            )
            n_ok += 1

        except Exception as e:
            logger.warning(f"Offre {doc.get('_id')} : erreur — {e}")
            n_err += 1

        # Flush batch
        if len(bulk_ops) >= batch_size:
            if not dry_run:
                collection.bulk_write(bulk_ops, ordered=False)
            bulk_ops.clear()

        # Log de progression toutes les 500 offres
        if i % 500 == 0:
            elapsed = time.time() - t_start
            rate = i / elapsed
            eta = (total - i) / rate if rate > 0 else 0
            logger.info(
                f"  {i}/{total} offres traitées "
                f"({rate:.1f} offres/s, ETA {eta/60:.1f} min)"
            )

    # Flush final
    if bulk_ops and not dry_run:
        collection.bulk_write(bulk_ops, ordered=False)

    elapsed = time.time() - t_start
    logger.info(
        f"{'[DRY-RUN] ' if dry_run else ''}"
        f"Terminé — {n_ok} enrichies, {n_err} erreurs, "
        f"durée totale : {elapsed:.1f}s ({elapsed/60:.1f} min)"
    )

    if dry_run:
        logger.info("DRY-RUN : aucune écriture en base effectuée.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enrichit les offres MongoDB avec skills_extraits via SBERT zero-shot."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-traite toutes les offres, même celles déjà enrichies.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nombre maximum d'offres à traiter (test).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Seuil de similarité cosine (défaut : 0.75).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcule sans écrire en MongoDB.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Taille des batches pour bulk_write MongoDB (défaut : 50).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(
        force=args.force,
        limit=args.limit,
        threshold=args.threshold,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
    )
