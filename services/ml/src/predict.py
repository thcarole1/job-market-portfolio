
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def recommend_offers(cv_text: str, top_n: int = 10) -> list:
    #1. Charger les 3 fichiers .pkl
    output_path = Path("services/ml/models")

    with open(f"{output_path}/tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    logger.info(f"Chargement du vectorizer réussie.")

    with open(f"{output_path}/tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    logger.info(f"Chargement de la matrice tfidf réussie.")

    with open(f"{output_path}/tfidf_ids.pkl", "rb") as f:
        ids = pickle.load(f)
    logger.info(f"Chargement des identifiants réussie.")

    # 2. Prendre le texte de ton CV en entrée
    # 3. Le vectoriser avec le même vectorizer
    cv_vector = vectorizer.transform([cv_text])
    logger.info(f"Vectorisation du CV réussie.")

    #4. Calculer la similarité cosinus entre le CV et chaque offre
    scores = cosine_similarity(cv_vector, tfidf_matrix).flatten()
    logger.info(f"Calcul des scores de similarité réussi.")

    #5. Retourner les top_n offres les plus similaires avec leurs ids et scores
    top_indices = scores.argsort()[::-1][:top_n]
    top_ids = [ids[i] for i in top_indices]
    logger.info(f"Récupération des {top_n} offres les plus similaires au texte entré.")

    return [{"id": ids[i], "score": float(scores[i])} for i in top_indices]
