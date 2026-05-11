from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from enum import Enum
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader

router = APIRouter()
loader = Mongoloader()
es_loader = Elasticloader()

@router.get("/")
def get_offers(
    contract_type: str | None = None,
    workplace_city: str | None = None,
    limit: int = 50,
    skip: int = 0
):
    '''
    GET /offers/ — liste des offres avec filtres.
    Utilise Elasticsearch pour la recherche full-text,
    MongoDB pour la pagination simple sans filtre.
    '''


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

        # ── Avec filtres → Elasticsearch ──────────────────
    if contract_type or workplace_city:
        must_clauses = []

        if contract_type:
            must_clauses.append({
                "match": {
                    "contract_type": {
                        "query": contract_type,
                        "fuzziness": "AUTO"  # tolère les fautes de frappe
                    }
                }
            })

        if workplace_city:
            must_clauses.append({
                "match": {
                    "workplace_label": {
                        "query": workplace_city,
                        "fuzziness": "AUTO"
                    }
                }
            })

        query = {"bool": {"must": must_clauses}}

        res = es_loader.es.search(
            index=es_loader.index_name,
            body={
                "query": query,
                "from": skip,
                "size": limit
            }
        )

        ids = [hit["_source"]["id"] for hit in res["hits"]["hits"]]

        if not ids:
            return []

        # Récupère les offres complètes depuis MongoDB
        offres = list(loader.db["offres_normalisees"].find(
            {"id": {"$in": ids}}, {"_id": 0}
        ))
        return offres


    # ── Sans filtre → MongoDB simple ──────────────────
    offres = list(loader.db["offres_normalisees"].find(
        {}, {"_id": 0}
    ).skip(skip).limit(limit))
    return offres

@router.get("/rome-labels")
def get_rome_labels():
    """Retourne la liste des rome_label uniques triés alphabétiquement."""
    rome_labels = loader.db["offres_normalisees"].distinct("rome_label")
    return sorted([r for r in rome_labels if r])


@router.get("/{id}")
def get_offer(id: str):
    '''GET /offers/{id}  — retourne le détail d'une offre depuis MongoDB'''
    #Suppression du champ _id de MongoDB qui n'est pas sérialisable en JSON
    offre = loader.db["offres_normalisees"].find_one({'id' : id}, {'_id' : 0})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offre
