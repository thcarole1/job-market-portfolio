import logging
from fastapi import APIRouter
from services.ingestion.src.loaders.mongo_loader import Mongoloader

logger = logging.getLogger(__name__)
router = APIRouter()
loader = Mongoloader()


def _build_match(rome_label: str | None = None,
                 ville: str | None = None,
                 periode: str | None = None) -> dict:
    """Construit le filtre MongoDB pour les agrégations."""
    match = {}
    if rome_label:
        match["rome_label"] = rome_label
    if ville:
        match["workplace_label"] = {"$regex": ville, "$options": "i"}
    if periode:
        match["creation_date"] = {"$regex": f"^{periode}"}
    return match


@router.get("/")
def get_stats(
    rome_label: str | None = None,
    ville: str | None = None,
    periode: str | None = None
):
    """
    Retourne les statistiques agrégées du marché de l'emploi.
    Paramètres optionnels : rome_label, ville, periode (ex: "2026-03")
    """
    match = _build_match(rome_label, ville, periode)
    match_stage = {"$match": match} if match else {"$match": {}}

    # ── Total ─────────────────────────────────────────
    total = loader.db["offres_normalisees"].count_documents(match)

    # ── Par type de contrat ───────────────────────────
    par_contrat = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$group": {"_id": "$contract_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    # ── Top 10 villes ─────────────────────────────────
    top_villes = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$group": {"_id": "$workplace_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))

    # ── Top 10 secteurs ───────────────────────────────
    top_secteurs = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$match": {"sector_activity_label": {"$ne": None}}},
        {"$group": {"_id": "$sector_activity_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))

    # ── Par expérience ────────────────────────────────
    exp_map = {"D": "Débutant", "S": "Souhaitée", "E": "Exigée"}
    par_experience = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$match": {"required_experience": {"$ne": None}}},
        {"$group": {"_id": "$required_experience", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    # ── Top 10 métiers ────────────────────────────────
    top_metiers = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$match": {"rome_label": {"$ne": None}}},
        {"$group": {"_id": "$rome_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))

    # ── Alternance ────────────────────────────────────
    alternance = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$group": {"_id": "$apprenticeship", "count": {"$sum": 1}}}
    ]))

    # ── Évolution mensuelle ───────────────────────────
    evolution = list(loader.db["offres_normalisees"].aggregate([
        match_stage,
        {"$match": {"creation_date": {"$ne": None}}},
        {"$group": {
            "_id": {"$substr": ["$creation_date", 0, 7]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]))

    return {
        "total":          total,
        "par_contrat":    [{"label": r["_id"] or "N/A", "count": r["count"]} for r in par_contrat],
        "top_villes":     [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_villes],
        "top_secteurs":   [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_secteurs],
        "par_experience": [{"label": exp_map.get(r["_id"], r["_id"] or "N/A"), "count": r["count"]} for r in par_experience],
        "top_metiers":    [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_metiers],
        "alternance":     [{"label": "Alternance" if r["_id"] else "Hors alternance", "count": r["count"]} for r in alternance],
        "evolution":      [{"label": r["_id"], "count": r["count"]} for r in evolution]
    }
