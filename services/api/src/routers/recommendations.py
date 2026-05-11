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

router = APIRouter()
loader = Mongoloader()
es_loader = Elasticloader()

class ExperienceLevel(str, Enum):
    debutant = "D"
    souhaitee = "S"
    exigee = "E"

class QueryRequest(BaseModel):
    query: str = Field(..., description="Texte de recherche ou contenu du CV", min_length=3)
    top_n: int = Field(10, description="Nombre d'offres à retourner", ge=1, le=50)
    contract_type: str | None = Field(None, description="Type de contrat : CDI, CDD, etc.")
    workplace_city: str | None = Field(None, description="Ville ou département")
    required_experience: ExperienceLevel | None = Field(None, description="D: débutant, S: souhaitée, E: exigée")
    source: str | None = Field(None, description="Source de l'offre : France_Travail, wttj...")
    rome_label: str | None = Field(None, description="Métier ex: Data engineer, Infirmier...")
    apprenticeship: bool | None = Field(None, description="Alternance uniquement")
    sector_activity_label: str | None = Field(None, description="Secteur d'activité")


def _build_es_filter(
    contract_type: str | None = None,
    workplace_city: str | None = None,
    required_experience: str | None = None,
    source: str | None = None,
    rome_label: str | None = None,
    apprenticeship: bool | None = None,
    sector_activity_label: str | None = None
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
    contract_type: str | None = None,
    workplace_city: str | None = None,
    required_experience: str | None = None,
    source: str | None = None,
    rome_label: str | None = None,
    apprenticeship: bool | None = None,
    sector_activity_label: str | None = None
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
        sector_activity_label=sector_activity_label
    )

    if not must:
        return None  # pas de filtre → toutes les offres

    body = {
        "query": {"bool": {"must": must}},
        "_source": ["id"],
        "size": 10000
    }

    res = es_loader.es.search(index=es_loader.index_name, body=body)
    ids = [hit["_source"]["id"] for hit in res["hits"]["hits"]]
    return ids  # [] si aucun résultat

def _get_offres(top_offres: list, model: str) -> list:
    """Récupère les offres complètes depuis MongoDB et ajoute score/detail."""
    offres_trouvees = []
    for offre in top_offres:
        result = loader.db["offres_normalisees"].find_one(
            {"id": offre.get("id")}, {"_id": 0, "embedding": 0}
        )
        if not result:
            continue
        result["score"] = offre.get("score_final") or offre.get("score")
        if model in ["hybrid", "knn"]:
            result["detail"] = offre.get("detail")
        offres_trouvees.append(result)
    return offres_trouvees


def _run_model(model: str, query: str, top_n: int, filtered_ids: list) -> list:
    """Sélectionne et lance le bon modèle."""
    if model == "sbert":
        return recommend_offers_sbert(query, top_n, filtered_ids)
    elif model == "hybrid":
        return recommend_offers_hybrid(query, top_n, filtered_ids)
    elif model == "knn":
        return recommend_offers_knn(query, top_n, filtered_ids)
    else:
        return recommend_offers(query, top_n, filtered_ids)

@router.post("/")
def get_offer(q: QueryRequest, model: str = "tfidf"):
    '''POST /recommend/ — recommande des offres à partir d'un texte + filtres'''
    filtered_ids = _get_filtered_ids(
        contract_type=q.contract_type,
        workplace_city=q.workplace_city,
        required_experience=q.required_experience.value if q.required_experience else None,
        source=q.source,
        rome_label=q.rome_label,
        apprenticeship=q.apprenticeship,
        sector_activity_label=q.sector_activity_label
    )
    if filtered_ids == []:
        return []

    top_offres = _run_model(model, q.query, q.top_n, filtered_ids)
    return _get_offres(top_offres, model)

@router.post("/cv")
async def recommend_from_cv(
    file: UploadFile = File(...),
    top_n: int = 10,
    contract_type: str | None = None,
    workplace_city: str | None = None,
    required_experience: ExperienceLevel | None = None,
    rome_label: str | None = None,
    apprenticeship: bool | None = None,
    sector_activity_label: str | None = None,
    model: str = "tfidf"
):
    if file.filename.endswith(".pdf"):
        cv_bytes = await file.read()
        cv_parsed = CVParser().parse(file_bytes=cv_bytes, file_type="pdf")
    else:
        raise HTTPException(status_code=422, detail="Format non supporté. Envoyez un fichier PDF.")

    filtered_ids = _get_filtered_ids(
        contract_type=contract_type,
        workplace_city=workplace_city,
        required_experience=required_experience.value if required_experience else None,
        rome_label=rome_label,
        apprenticeship=apprenticeship,
        sector_activity_label=sector_activity_label
    )
    if filtered_ids == []:
        return []

    top_offres = _run_model(model, cv_parsed, top_n, filtered_ids)
    return _get_offres(top_offres, model)
