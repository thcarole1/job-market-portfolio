from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from enum import Enum
from services.ingestion.src.loaders.mongo_loader import Mongoloader

router = APIRouter()
loader = Mongoloader()

@router.get("/")
def get_offers(
    contract_type: str | None = None,
    workplace_city: str | None = None,
    limit: int = 50,
    skip: int = 0
):
    '''
    Explication :

    limit = 50   → retourne 50 offres par page
    skip = 0     → page 1 : offres 0 à 49
    skip = 50    → page 2 : offres 50 à 99
    skip = 100   → page 3 : offres 100 à 149

    En MongoDB :
    .skip(0).limit(50)   # page 1
    .skip(50).limit(50)  # page 2
    '''
    # On filtre d'abord (si filtre existe)
    query_filter = {}
    if contract_type:
        query_filter["contract_type"] = {"$regex": contract_type, "$options": "i"}
    if workplace_city:
        query_filter["workplace_label"] = {"$regex": workplace_city, "$options": "i"}

    offres = list(loader.db["offres_normalisees"].find(query_filter, {"_id": 0}).skip(skip).limit(limit))
    return offres


@router.get("/{id}")
def get_offer(id: str):
    '''GET /offers/{id}  — retourne le détail d'une offre depuis MongoDB'''
    #Suppression du champ _id de MongoDB qui n'est pas sérialisable en JSON
    offre = loader.db["offres_normalisees"].find_one({'id' : id}, {'_id' : 0})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offre
