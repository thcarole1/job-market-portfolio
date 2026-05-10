import numpy as np
import logging
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.hybrid_scorer import HybridScorer
from services.ml.src.cv_structurer import CVStructurer
from services.ml.src.encoder import get_model

logger = logging.getLogger(__name__)

def recommend_offers_hybrid(cv_text: str, top_n: int = 10,
                             offer_ids: list = None) -> list:
    """
    Recommande les offres avec scoring hybride.
    - Récupère les embeddings depuis Elasticsearch
    - Applique HybridScorer sur toutes les offres
    offer_ids : liste d'ids pré-filtrés (ville, contrat...)
    Retourne liste de {id, score_final, detail}.
    """
    # Structuration et embedding du CV
    cv_structured = CVStructurer().extract(cv_text)
    model         = get_model()
    cv_embedding  = model.encode([cv_text])

    # Connexion ES
    es_loader = Elasticloader()

    # Récupère les offres avec embeddings depuis ES
    query_filter = {}
    if offer_ids is not None:
        query_filter = {"ids": {"values": offer_ids}}

    body = {
        "query":   query_filter if query_filter else {"match_all": {}},
        "_source": True,  # ← inclut tous les champs dont embedding
        "size":    10000
    }

    res  = es_loader.es.search(index=es_loader.index_name, body=body)
    hits = res["hits"]["hits"]

    if not hits:
        return []

    # Scoring hybride sur chaque offre
    scorer  = HybridScorer()
    results = []

    for hit in hits:
        offre          = hit["_source"]
        offre_embedding = np.array(offre.get("embedding", [])).reshape(1, -1)

        # Supprime l'embedding de l'offre avant de la retourner
        offre_sans_embedding = {k: v for k, v in offre.items() if k != "embedding"}

        scoring = scorer.score(cv_structured, cv_embedding, offre_sans_embedding, offre_embedding)

        results.append({
            "id":          offre["id"],
            "score_final": scoring["score_final"],
            "detail":      scoring["detail"]
        })

    sorted_results = sorted(results, key=lambda x: x["score_final"], reverse=True)
    return sorted_results[:top_n]
