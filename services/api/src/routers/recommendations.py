from fastapi import APIRouter,HTTPException, UploadFile, File
from pydantic import BaseModel,Field
from enum import Enum

from services.ml.src.predict import recommend_offers
from services.ml.src.predict_sbert import recommend_offers_sbert
from services.ml.src.predict_hybrid import recommend_offers_hybrid
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

@router.post("/")
def get_offer(q:QueryRequest,model: str = "tfidf"):
    '''POST /recommend/query  — recommande des offres à partir d'un texte + filtres'''
    # On filtre d'abord (si filtre existe) et seulement ensuite on fait le scoring
    query_filter = {}
    if q.contract_type:
        query_filter["contract_type"] = {"$regex": q.contract_type, "$options": "i"}
    if q.workplace_city:
        query_filter["workplace_label"] = {"$regex": q.workplace_city, "$options": "i"}
    if q.required_experience:
        query_filter["required_experience"] = q.required_experience.value  # ← .value extrait "D", "S" ou "E"
    if q.source:
        query_filter["source"] = {"$regex": q.source, "$options": "i"}

    filtered_ids = None
    if query_filter:
        filtered_ids = [
            o["id"] for o in loader.db["offres_normalisees"].find(query_filter, {"id": 1, "_id": 0})]

        if len(filtered_ids) == 0:
            return []  # ← aucun résultat pour ce filtre

    # Recherche des offres similaires à la requête utilisateur
    if model == "sbert":
        top_offres = recommend_offers_sbert(q.query, q.top_n, filtered_ids)
    elif model == "hybrid":
        top_offres = recommend_offers_hybrid(q.query, q.top_n, filtered_ids)
    else:
        top_offres = recommend_offers(q.query, q.top_n, filtered_ids)

    offres_trouvees = []
    for offre in top_offres:
        result = loader.db["offres_normalisees"].find_one({'id' : offre.get('id')}, {'_id' : 0})
        if not result:
            continue # offre non trouvée → on passe à la suivante
        # ← score_final pour hybrid, score pour tfidf/sbert
        result["score"] = offre.get("score_final") or offre.get("score")
        if model == "hybrid":
            result["detail"] = offre.get("detail")
        offres_trouvees.append(result)

    return offres_trouvees


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
        cv_parsed = CVParser().parse(file_bytes = cv_bytes,file_type = "pdf")
    else:
        raise HTTPException(status_code=422, detail="Format non supporté. Envoyez un fichier PDF.")

    # On filtre d'abord (si filtre existe) et seulement ensuite on fait le scoring
    query_filter = {}
    if contract_type:
        query_filter["contract_type"] = {"$regex": contract_type, "$options": "i"}
    if workplace_city:
        query_filter["workplace_label"] = {"$regex": workplace_city, "$options": "i"}

    filtered_ids = None
    if query_filter:
        filtered_ids = [
            o["id"] for o in loader.db["offres_normalisees"].find(query_filter, {"id": 1, "_id": 0})]

        if len(filtered_ids) == 0:
            return []  # ← aucun résultat pour ce filtre

    # Recherche des offres similaires à la requête utilisateur
        # Remplace l'appel à recommend_offers par :
    if model == "sbert":
        top_offres = recommend_offers_sbert(cv_parsed, top_n, filtered_ids)
    elif model == "hybrid":
        top_offres = recommend_offers_hybrid(cv_parsed, top_n, filtered_ids)
    else:
        top_offres = recommend_offers(cv_parsed, top_n, filtered_ids)

    offres_trouvees = []
    for offre in top_offres:
        result = loader.db["offres_normalisees"].find_one({'id' : offre.get('id')}, {'_id' : 0})
        if not result:
            continue # offre non trouvée → on passe à la suivante
        result["score"] = offre.get("score_final") or offre.get("score")
        if model == "hybrid":
            result["detail"] = offre.get("detail")
        offres_trouvees.append(result)

    return offres_trouvees
