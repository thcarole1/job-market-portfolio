from fastapi import APIRouter,HTTPException
from services.ingestion.src.loaders.mongo_loader import Mongoloader

router = APIRouter()
loader = Mongoloader()


@router.get("/{id}")
def get_offer(id: str):
    '''GET /offers/{id}  — retourne le détail d'une offre depuis MongoDB'''
    #Suppression du champ _id de MongoDB qui n'est pas sérialisable en JSON
    offre = loader.db["offres_normalisees"].find_one({'id' : id}, {'_id' : 0})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offre
