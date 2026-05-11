import numpy as np
import logging
from sklearn.metrics.pairwise import cosine_similarity
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.hybrid_scorer import HybridScorer
from services.ml.src.cv_structurer import CVStructurer
from services.ml.src.encoder import get_model

logger = logging.getLogger(__name__)

def recommend_offers_hybrid(cv_text: str, top_n: int = 10,
                             offer_ids: list = None,
                             show_detail: bool = True) -> list:
    """
    Recommande les offres avec scoring hybride.
    - show_detail=True  → HybridScorer complet (5 critères pondérés)
    - show_detail=False → Cosine SBERT uniquement (plus rapide)
    """
    # Embedding du CV
    model        = get_model()
    cv_embedding = model.encode([cv_text])

    # Structuration du CV — uniquement si détail demandé
    cv_structured = CVStructurer().extract(cv_text) if show_detail else None

    # Connexion ES
    es_loader    = Elasticloader()
    query_filter = {"ids": {"values": offer_ids}} if offer_ids is not None else {}

    body = {
        "query":   query_filter if query_filter else {"match_all": {}},
        "_source": True,
        "size":    10000
    }

    res  = es_loader.es.search(index=es_loader.index_name, body=body)
    hits = res["hits"]["hits"]

    if not hits:
        return []

    scorer  = HybridScorer()
    results = []

    for hit in hits:
        offre           = hit["_source"]
        offre_embedding = np.array(offre.get("embedding", [])).reshape(1, -1)
        offre_sans_embedding = {k: v for k, v in offre.items() if k != "embedding"}

        if show_detail:
            # HybridScorer complet — 5 critères pondérés
            scoring = scorer.score(cv_structured, cv_embedding, offre_sans_embedding, offre_embedding)
            results.append({
                "id":          offre["id"],
                "score_final": scoring["score_final"],
                "detail":      scoring["detail"]
            })
        else:
            # Cosine SBERT uniquement — rapide
            score = float(cosine_similarity(cv_embedding, offre_embedding)[0][0])
            results.append({
                "id":          offre["id"],
                "score_final": score,
                "detail":      None
            })

    sorted_results = sorted(results, key=lambda x: x["score_final"], reverse=True)
    return sorted_results[:top_n]
