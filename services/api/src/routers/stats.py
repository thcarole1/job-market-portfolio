import logging
from fastapi import APIRouter
from services.ingestion.src.loaders.mongo_loader import Mongoloader

logger = logging.getLogger(__name__)
router = APIRouter()
loader = Mongoloader()

# Labels lisibles pour les types de contrat
CONTRACT_LABELS = {
    "CDI": "CDI — Contrat à durée indéterminée",
    "CDD": "CDD — Contrat à durée déterminée",
    "MIS": "Intérim / Mission",
    "LIB": "Profession libérale",
    "SAI": "Saisonnier",
    "CCE": "Commission / Courtage",
    "FRA": "Franchise",
    "DIN": "Contrat de travail intermittent",
    "DDI": "Insertion par l'activité économique",
    "REP": "Reprise d'entreprise",
    "TTI": "Travail temporaire insertion",
    "DDT": "Contrat à durée déterminée d'usage",
}

EXP_MAP = {"D": "Débutant", "S": "Souhaitée", "E": "Exigée"}


def _build_match(
    rome_label: str | None = None,
    ville:      str | None = None,
    periode:    str | None = None,
) -> dict:
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
    ville:      str | None = None,
    periode:    str | None = None,
):
    """
    Retourne les statistiques agrégées du marché de l'emploi.
    Paramètres optionnels : rome_label, ville, periode (ex: "2026-03")
    """
    match       = _build_match(rome_label, ville, periode)
    match_stage = {"$match": match} if match else {"$match": {}}
    col         = loader.db["offres_normalisees"]

    # ── Total ──────────────────────────────────────────────────────────────
    total = col.count_documents(match)

    # ── Par type de contrat ────────────────────────────────────────────────
    par_contrat = list(col.aggregate([
        match_stage,
        {"$group": {"_id": "$contract_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]))

    # ── Top 10 villes ──────────────────────────────────────────────────────
    top_villes = list(col.aggregate([
        match_stage,
        {"$group": {"_id": "$workplace_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]))

    # ── Top 10 secteurs ────────────────────────────────────────────────────
    top_secteurs = list(col.aggregate([
        match_stage,
        {"$match": {"sector_activity_label": {"$ne": None}}},
        {"$group": {"_id": "$sector_activity_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]))

    # ── Par expérience ─────────────────────────────────────────────────────
    par_experience = list(col.aggregate([
        match_stage,
        {"$match": {"required_experience": {"$ne": None}}},
        {"$group": {"_id": "$required_experience", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]))

    # ── Top 10 métiers ─────────────────────────────────────────────────────
    top_metiers = list(col.aggregate([
        match_stage,
        {"$match": {"rome_label": {"$ne": None}}},
        {"$group": {"_id": "$rome_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]))

    # ── Alternance ─────────────────────────────────────────────────────────
    alternance = list(col.aggregate([
        match_stage,
        {"$group": {"_id": "$apprenticeship", "count": {"$sum": 1}}},
    ]))

    # ── Évolution mensuelle ────────────────────────────────────────────────
    evolution = list(col.aggregate([
        match_stage,
        {"$match": {"creation_date": {"$ne": None}}},
        {"$group": {
            "_id":   {"$substr": ["$creation_date", 0, 7]},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))

    # ── Top 20 hard skills ─────────────────────────────────────────────────
    top_competences = list(col.aggregate([
        match_stage,
        {"$match": {"competences_detectees": {"$ne": None, "$ne": []}}},
        {"$unwind": "$competences_detectees"},
        {"$group": {"_id": "$competences_detectees", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]))

    # ── Top 15 soft skills explicites ──────────────────────────────────────
    top_soft_explicites = list(col.aggregate([
        match_stage,
        {"$match": {"skills_extraits.soft_explicites": {"$exists": True, "$ne": []}}},
        {"$unwind": "$skills_extraits.soft_explicites"},
        {"$group": {"_id": "$skills_extraits.soft_explicites", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]))

    # ── Top 10 soft skills implicites ──────────────────────────────────────
    top_soft_implicites = list(col.aggregate([
        match_stage,
        {"$match": {"skills_extraits.soft_implicites": {"$exists": True, "$ne": []}}},
        {"$unwind": "$skills_extraits.soft_implicites"},
        {"$group": {"_id": "$skills_extraits.soft_implicites", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]))

    # ── Transparence salariale ─────────────────────────────────────────────
    avec_salaire  = col.count_documents({**match, "salary_label": {"$ne": None}})
    taux_salaire  = round(avec_salaire / total * 100, 1) if total > 0 else 0

    # ── Couverture skills_extraits ─────────────────────────────────────────
    avec_skills   = col.count_documents({**match, "skills_extraits": {"$exists": True}})
    taux_skills   = round(avec_skills / total * 100, 1) if total > 0 else 0

    return {
        "total":               total,
        "avec_salaire":        avec_salaire,
        "taux_salaire":        taux_salaire,
        "avec_skills":         avec_skills,
        "taux_skills":         taux_skills,
        "par_contrat":         [
            {
                "label": CONTRACT_LABELS.get(r["_id"], r["_id"] or "N/A"),
                "code":  r["_id"] or "N/A",
                "count": r["count"],
            }
            for r in par_contrat
        ],
        "top_villes":          [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_villes],
        "top_secteurs":        [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_secteurs],
        "par_experience":      [{"label": EXP_MAP.get(r["_id"], r["_id"] or "N/A"), "count": r["count"]} for r in par_experience],
        "top_metiers":         [{"label": r["_id"] or "N/A", "count": r["count"]} for r in top_metiers],
        "alternance":          [{"label": "Alternance" if r["_id"] else "Hors alternance", "count": r["count"]} for r in alternance],
        "evolution":           [{"label": r["_id"], "count": r["count"]} for r in evolution],
        "top_competences":     [{"label": r["_id"], "count": r["count"]} for r in top_competences],
        "top_soft_explicites": [{"label": r["_id"], "count": r["count"]} for r in top_soft_explicites],
        "top_soft_implicites": [{"label": r["_id"], "count": r["count"]} for r in top_soft_implicites],
    }
