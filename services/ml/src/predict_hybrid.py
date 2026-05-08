import numpy as np
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

from services.ingestion.src.loaders.mongo_loader import Mongoloader
from services.ml.src.hybrid_scorer import HybridScorer
from services.ml.src.cv_parser import CVParser
from services.ml.src.cv_structurer import CVStructurer

ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT / "services/ml/models"
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

def recommend_offers_hybrid(cv_text: str, top_n: int = 10,
                             offer_ids: list = None) -> list:
    """
    Recommande les offres avec scoring hybride.
    offer_ids : liste d'ids pré-filtrés (ville, contrat...)
            Si None, score toutes les offres.
    Retourne liste de {id, score_final, detail}.
    """
    cv_structured = CVStructurer().extract(cv_text)

    # Embedding CV
    model = SentenceTransformer(MODEL_NAME)
    cv_embedding = model.encode([cv_text])

    # Chargement
    loader = Mongoloader()

    # Filtrage des offres MongoDB (si nécessaire)
    query = {}
    if offer_ids is not None:
        query = {"id": {"$in": offer_ids}}
    offres = list(loader.db["offres_normalisees"].find(query, {"_id": 0}))

    # Embeddings offres
    sbert_embeddings = np.load(f"{MODELS_DIR}/sbert_embeddings.npy")
    with open(f"{MODELS_DIR}/sbert_ids.pkl", "rb") as f:
        sbert_ids = pickle.load(f)

    scorer = HybridScorer()
    results=[]
    for offre in offres:
        resultat = {}
        idx = sbert_ids.index(offre["id"]) if offre["id"] in sbert_ids else None
        if idx is None:
            continue
        offre_embedding = sbert_embeddings[idx:idx+1]
        scoring = scorer.score(cv_structured, cv_embedding, offre, offre_embedding)

        resultat['id']=offre['id']
        resultat['score_final']=scoring['score_final']
        resultat['detail']=scoring['detail']

        results.append(resultat)
    sorted_results = sorted(results, key=lambda x : x["score_final"], reverse=True)
    return sorted_results[:top_n]
