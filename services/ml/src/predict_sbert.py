import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.ingestion.src.loaders.elastic_loader import Elasticloader
from services.ml.src.encoder import get_model

logger = logging.getLogger(__name__)

def recommend_offers_sbert(cv_text: str, top_n: int = 10, offer_ids: list = None) -> list:
    """
    Recommande les offres les plus similaires au texte du CV
    en utilisant les embeddings SBERT stockés dans Elasticsearch.
    Retourne une liste de dicts {id, score} triés par score décroissant.
    """
    # Encode le CV
    model = get_model()
    cv_embedding = model.encode([cv_text])

    # Connexion ES
    es_loader = Elasticloader()

    # Récupère les offres avec leurs embeddings depuis ES
    query_filter = {}
    if offer_ids is not None:
        query_filter = {"ids": {"values": offer_ids}}

    body = {
        "query": query_filter if query_filter else {"match_all": {}},
        "_source": ["id", "embedding"],
        "size": 10000  # récupère toutes les offres
    }

    res = es_loader.es.search(index=es_loader.index_name, body=body)
    hits = res["hits"]["hits"]

    if not hits:
        return []

    # Extrait ids et embeddings
    ids        = [hit["_source"]["id"] for hit in hits]
    embeddings = np.array([hit["_source"]["embedding"] for hit in hits])

    # Calcul similarité cosinus
    scores     = cosine_similarity(cv_embedding, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:top_n]

    return [{"id": ids[i], "score": float(scores[i])} for i in top_indices]
