import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.encoder import get_model, MODEL_NAME
from services.ml.src.hybrid_scorer import HybridScorer
from services.ml.src.cv_structurer import CVStructurer

logger = logging.getLogger(__name__)

def recommend_offers_knn(cv_text: str, top_n: int = 10,
                         offer_ids: list = None) -> list:
    """
    Recommande les offres via KNN search dans Elasticsearch.
    - Encode le CV avec SBERT
    - Recherche les top_n * 5 offres les plus proches via KNN ES
    - Applique HybridScorer sur les résultats pour le détail
    - Retourne liste de {id, score_final, detail}
    """
    # Encode le CV
    model = get_model()
    cv_embedding = model.encode(cv_text)
    cv_structured = CVStructurer().extract(cv_text)

    # Connexion ES
    es_loader = Elasticloader()

    # Requête KNN — récupère plus de candidats pour le rescoring
    knn_k = min(top_n * 5, 100)  # max 100 candidats

    knn_clause = {
        "field":          "embedding",
        "query_vector":   cv_embedding.tolist(),
        "k":              knn_k,
        "num_candidates": knn_k * 10
    }

    if offer_ids:
        knn_clause["filter"] = {"ids": {"values": offer_ids}}  # ← dict directement, pas de liste

    query = {"knn": knn_clause}

    res = es_loader.es.search(
        index=es_loader.index_name,
        body=query,
        size=knn_k
    )

    # Récupère les offres complètes depuis MongoDB
    ids_knn = [hit["_source"]["id"] for hit in res["hits"]["hits"]]
    loader = Mongoloader()
    offres = list(loader.db["offres_normalisees"].find(
        {"id": {"$in": ids_knn}}, {"_id": 0, "embedding": 0}
    ))

    # Applique HybridScorer sur les candidats KNN
    scorer = HybridScorer()
    results = []
    for offre in offres:
        # Récupère l'embedding de l'offre depuis ES
        hit = next((h for h in res["hits"]["hits"] if h["_source"]["id"] == offre["id"]), None)
        if hit is None:
            continue
        offre_embedding = np.array(hit["_source"].get("embedding", [])).reshape(1, -1)
        cv_embedding_2d = cv_embedding.reshape(1, -1)

        scoring = scorer.score(cv_structured, cv_embedding_2d, offre, offre_embedding)
        results.append({
            "id":          offre["id"],
            "score_final": scoring["score_final"],
            "score":       scoring["score_final"],
            "detail":      scoring["detail"]
        })

    # Trie par score_final et retourne top_n
    results = sorted(results, key=lambda x: x["score_final"], reverse=True)
    return results[:top_n]
