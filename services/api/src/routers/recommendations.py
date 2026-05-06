from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from enum import Enum

from services.ml.src.predict import recommend_offers
from services.ingestion.src.loaders.mongo_loader import Mongoloader

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
def get_offer(q:QueryRequest):
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
    top_offres = recommend_offers(q.query, q.top_n,filtered_ids)
    scores_by_id = {o["id"]: o["score"] for o in top_offres}
    offres_trouvees = []
    for offre in top_offres:
        result = loader.db["offres_normalisees"].find_one({'id' : offre.get('id')}, {'_id' : 0})
        if not result:
            continue # offre non trouvée → on passe à la suivante
        else:
            result["score"] = scores_by_id[result["id"]]  # ← ajoute le score à l'offre
            offres_trouvees.append(result)

    return offres_trouvees
