import logging
import numpy as np
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.encoder import get_model
from services.ml.src.hybrid_scorer import HybridScorer
from services.ml.src.cv_structurer import CVStructurer

logger = logging.getLogger(__name__)

def recommend_offers_knn(cv_text: str, top_n: int = 10,
                         offer_ids: list = None,
                         show_detail: bool = True) -> list:
    """
    Recommande les offres via KNN search dans Elasticsearch.
    - show_detail=True  → KNN pré-filtrage + HybridScorer complet
    - show_detail=False → KNN score uniquement (plus rapide)
    """
    # Encode le CV
    model        = get_model()
    cv_embedding = model.encode(cv_text)

    # Structuration du CV — uniquement si détail demandé
    cv_structured = CVStructurer().extract(cv_text) if show_detail else None

    # Connexion ES
    es_loader = Elasticloader()

    # Requête KNN
    knn_k = min(top_n * 5, 100)

    knn_clause = {
        "field":          "embedding",
        "query_vector":   cv_embedding.tolist(),
        "k":              knn_k,
        "num_candidates": knn_k * 10
    }

    if offer_ids:
        knn_clause["filter"] = {"ids": {"values": offer_ids}}

    res = es_loader.es.search(
        index=es_loader.index_name,
        body={"knn": knn_clause},
        size=knn_k
    )

    hits = res["hits"]["hits"]
    if not hits:
        return []

    if show_detail:
        # Récupère les offres complètes depuis MongoDB
        ids_knn = [hit["_source"]["id"] for hit in hits]
        loader  = Mongoloader()
        offres  = list(loader.db["offres_normalisees"].find(
            {"id": {"$in": ids_knn}}, {"_id": 0, "embedding": 0}
        ))

        # HybridScorer sur les candidats KNN
        scorer      = HybridScorer()
        results     = []
        cv_emb_2d   = cv_embedding.reshape(1, -1)

        for offre in offres:
            hit = next((h for h in hits if h["_source"]["id"] == offre["id"]), None)
            if hit is None:
                continue
            offre_embedding = np.array(hit["_source"].get("embedding", [])).reshape(1, -1)
            scoring = scorer.score(cv_structured, cv_emb_2d, offre, offre_embedding)
            results.append({
                "id":          offre["id"],
                "score_final": scoring["score_final"],
                "score":       scoring["score_final"],
                "detail":      scoring["detail"]
            })
    else:
        # KNN score ES → cosine similarity pur
        results = [{
            "id":          hit["_source"]["id"],
            "score_final": round(2 * hit["_score"] - 1, 3),  # ← reconvertit ES → cosine
            "score":       round(2 * hit["_score"] - 1, 3),
            "detail":      None
        } for hit in hits]

    results = sorted(results, key=lambda x: x["score_final"], reverse=True)
    return results[:top_n]
