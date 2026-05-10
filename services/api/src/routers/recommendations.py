from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from enum import Enum

from services.ml.src.predict import recommend_offers
from services.ml.src.predict_sbert import recommend_offers_sbert
from services.ml.src.predict_hybrid import recommend_offers_hybrid
from services.ml.src.predict_knn import recommend_offers_knn
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.cv_parser import CVParser

router = APIRouter()
loader = Mongoloader()

class ExperienceLevel(str, Enum):
    debutant = "D"
    souhaitee = "S"
    exigee = "E"

class QueryRequest(BaseModel):
    query: str = Field(..., description="Texte de recherche ou contenu du CV", min_length=3)
    top_n: int = Field(10, description="Nombre d'offres à retourner", ge=1, le=50)
    contract_type: str | None = Field(None, description="Type de contrat : CDI, CDD, etc.")
    workplace_city: str | None = Field(None, description="Code INSEE de la ville")
    required_experience: ExperienceLevel | None = Field(None, description="D: débutant, S: souhaitée, E: exigée")
    source: str | None = Field(None, description="Source de l'offre : France_Travail, wttj...")


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
    query_filter = {}
    if q.contract_type:
        query_filter["contract_type"] = {"$regex": q.contract_type, "$options": "i"}
    if q.workplace_city:
        query_filter["workplace_label"] = {"$regex": q.workplace_city, "$options": "i"}
    if q.required_experience:
        query_filter["required_experience"] = q.required_experience.value
    if q.source:
        query_filter["source"] = {"$regex": q.source, "$options": "i"}

    filtered_ids = None
    if query_filter:
        filtered_ids = [
            o["id"] for o in loader.db["offres_normalisees"].find(query_filter, {"id": 1, "_id": 0})
        ]
        if len(filtered_ids) == 0:
            return []

    top_offres = _run_model(model, q.query, q.top_n, filtered_ids)
    return _get_offres(top_offres, model)


@router.post("/cv")
async def recommend_from_cv(
    file: UploadFile = File(...),
    top_n: int = 10,
    contract_type: str | None = None,
    workplace_city: str | None = None,
    model: str = "tfidf"
):
    if file.filename.endswith(".pdf"):
        cv_bytes = await file.read()
        cv_parsed = CVParser().parse(file_bytes=cv_bytes, file_type="pdf")
    else:
        raise HTTPException(status_code=422, detail="Format non supporté. Envoyez un fichier PDF.")

    query_filter = {}
    if contract_type:
        query_filter["contract_type"] = {"$regex": contract_type, "$options": "i"}
    if workplace_city:
        query_filter["workplace_label"] = {"$regex": workplace_city, "$options": "i"}

    filtered_ids = None
    if query_filter:
        filtered_ids = [
            o["id"] for o in loader.db["offres_normalisees"].find(query_filter, {"id": 1, "_id": 0})
        ]
        if len(filtered_ids) == 0:
            return []

    top_offres = _run_model(model, cv_parsed, top_n, filtered_ids)
    return _get_offres(top_offres, model)
