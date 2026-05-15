from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from enum import Enum

from services.ml.src.predict import recommend_offers
from services.ml.src.predict_sbert import recommend_offers_sbert
from services.ml.src.predict_hybrid import recommend_offers_hybrid
from services.ml.src.predict_knn import recommend_offers_knn
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.cv_parser import CVParser
from services.ml.src.cv_structurer import CVStructurer
from services.ml.src.skills_extractor import SkillsExtractor

router    = APIRouter()
loader    = Mongoloader()
es_loader = Elasticloader()


class ExperienceLevel(str, Enum):
    debutant  = "D"
    souhaitee = "S"
    exigee    = "E"


class QueryRequest(BaseModel):
    query:                 str            = Field(..., description="Texte de recherche ou contenu du CV", min_length=3)
    top_n:                 int            = Field(10, description="Nombre d'offres à retourner", ge=1, le=50)
    contract_type:         str | None     = Field(None, description="Type de contrat : CDI, CDD, etc.")
    workplace_city:        str | None     = Field(None, description="Ville ou département")
    required_experience:   ExperienceLevel | None = Field(None, description="D: débutant, S: souhaitée, E: exigée")
    source:                str | None     = Field(None, description="Source de l'offre")
    rome_label:            str | None     = Field(None, description="Métier ex: Data engineer, Infirmier...")
    apprenticeship:        bool | None    = Field(None, description="Alternance uniquement")
    sector_activity_label: str | None     = Field(None, description="Secteur d'activité")
    show_detail:           bool           = Field(True, description="Afficher l'analyse de compatibilité")


def _build_es_filter(
    contract_type:         str | None  = None,
    workplace_city:        str | None  = None,
    required_experience:   str | None  = None,
    source:                str | None  = None,
    rome_label:            str | None  = None,
    apprenticeship:        bool | None = None,
    sector_activity_label: str | None  = None,
) -> list:
    """Construit les clauses de filtre ES."""
    must = []
    if contract_type:
        must.append({"term": {"contract_type": contract_type.upper()}})
    if workplace_city:
        must.append({"match": {"workplace_label": {"query": workplace_city, "fuzziness": "AUTO"}}})
    if required_experience:
        must.append({"term": {"required_experience": required_experience}})
    if source:
        must.append({"term": {"source": source}})
    if rome_label:
        must.append({"match": {"rome_label": {"query": rome_label, "fuzziness": "AUTO"}}})
    if apprenticeship is not None:
        must.append({"term": {"apprenticeship": apprenticeship}})
    if sector_activity_label:
        must.append({"match": {"sector_activity_label": {"query": sector_activity_label, "fuzziness": "AUTO"}}})
    return must


def _get_filtered_ids(
    contract_type:         str | None  = None,
    workplace_city:        str | None  = None,
    required_experience:   str | None  = None,
    source:                str | None  = None,
    rome_label:            str | None  = None,
    apprenticeship:        bool | None = None,
    sector_activity_label: str | None  = None,
) -> list | None:
    """
    Retourne les ids filtrés via Elasticsearch.
    Retourne None si pas de filtre → toutes les offres.
    Retourne [] si filtre actif mais aucun résultat.
    """
    must = _build_es_filter(
        contract_type=contract_type,
        workplace_city=workplace_city,
        required_experience=required_experience,
        source=source,
        rome_label=rome_label,
        apprenticeship=apprenticeship,
        sector_activity_label=sector_activity_label,
    )
    if not must:
        return None

    body = {
        "query": {"bool": {"must": must}},
        "_source": ["id"],
        "size": 10000,
    }
    res = es_loader.es.search(index=es_loader.index_name, body=body)
    return [hit["_source"]["id"] for hit in res["hits"]["hits"]]


def _get_offres(
    top_offres:    list,
    model:         str,
    show_detail:   bool        = True,
    cv_structured: dict | None = None,
) -> list:
    """
    Récupère les offres complètes depuis MongoDB et ajoute score/detail.

    Si cv_structured est fourni et show_detail=True, calcule le gap
    hard/soft skills entre le CV et chaque offre via SkillsExtractor.
    """
    extractor = SkillsExtractor.get_instance() if cv_structured else None

    offres_trouvees = []
    for offre in top_offres:
        result = loader.db["offres_normalisees"].find_one(
            {"id": offre.get("id")},
            {"_id": 0, "embedding": 0},
        )
        if not result:
            continue

        result["score"] = offre.get("score_final") or offre.get("score")

        if model in ["hybrid", "knn"] and show_detail:
            result["detail"] = offre.get("detail")

        # Gap skills CV/offre — toujours présent si CV structuré disponible
        if extractor and result.get("skills_extraits"):
            cv_all_skills = (
                [s.lower() for s in cv_structured.get("hard_skills", [])]
                + [s.lower() for s in cv_structured.get("soft_skills", [])]
            )
            result["skills_gap"] = extractor.compute_gap(
                cv_skills=cv_all_skills,
                offer_result=result["skills_extraits"],
            )

        offres_trouvees.append(result)

    return offres_trouvees


def _run_model(
    model:        str,
    query:        str,
    top_n:        int,
    filtered_ids: list,
    show_detail:  bool = True,
) -> list:
    """Sélectionne et lance le bon modèle."""
    if model == "sbert":
        return recommend_offers_sbert(query, top_n, filtered_ids)
    elif model == "hybrid":
        return recommend_offers_hybrid(query, top_n, filtered_ids, show_detail=show_detail)
    elif model == "knn":
        return recommend_offers_knn(query, top_n, filtered_ids, show_detail=show_detail)
    else:
        return recommend_offers(query, top_n, filtered_ids)


@router.post("/")
def get_offer(q: QueryRequest, model: str = "tfidf"):
    """POST /recommend/ — recommande des offres à partir d'un texte + filtres."""
    filtered_ids = _get_filtered_ids(
        contract_type=q.contract_type,
        workplace_city=q.workplace_city,
        required_experience=q.required_experience.value if q.required_experience else None,
        source=q.source,
        rome_label=q.rome_label,
        apprenticeship=q.apprenticeship,
        sector_activity_label=q.sector_activity_label,
    )
    if filtered_ids == []:
        return []

    top_offres = _run_model(model, q.query, q.top_n, filtered_ids, show_detail=q.show_detail)
    # Pas de cv_structured sur cet endpoint — pas de skills_gap
    return _get_offres(top_offres, model, show_detail=q.show_detail)


@router.post("/cv")
async def recommend_from_cv(
    file:                  UploadFile = File(...),
    top_n:                 int        = 10,
    contract_type:         str | None = None,
    workplace_city:        str | None = None,
    required_experience:   ExperienceLevel | None = None,
    rome_label:            str | None = None,
    apprenticeship:        bool | None = None,
    sector_activity_label: str | None = None,
    model:                 str        = "tfidf",
    show_detail:           bool       = True,
):
    """POST /recommend/cv — recommande des offres à partir d'un CV PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Format non supporté. Envoyez un fichier PDF.")

    # 1. Parsing PDF → texte brut
    cv_bytes  = await file.read()
    cv_parsed = CVParser().parse(file_bytes=cv_bytes, file_type="pdf")

    # 2. Structuration CV — hard skills + soft skills (SBERT zero-shot)
    #    Le modèle SBERT est déjà chargé via le lifespan de l'API → pas de latence
    cv_structured = CVStructurer().extract(cv_parsed)

    filtered_ids = _get_filtered_ids(
        contract_type=contract_type,
        workplace_city=workplace_city,
        required_experience=required_experience.value if required_experience else None,
        rome_label=rome_label,
        apprenticeship=apprenticeship,
        sector_activity_label=sector_activity_label,
    )
    if filtered_ids == []:
        return []

    # 3. Recommandation
    top_offres = _run_model(model, cv_parsed, top_n, filtered_ids, show_detail=show_detail)

    # 4. Enrichissement avec gap skills (toujours présent avec un CV)
    return _get_offres(
        top_offres,
        model,
        show_detail=show_detail,
        cv_structured=cv_structured,
    )
