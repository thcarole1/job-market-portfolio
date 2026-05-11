from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from services.api.src.routers import jobs, recommendations, stats
from services.ml.src.encoder import get_model

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Préchauffage au démarrage — libération des ressources à l'arrêt."""
    logger.info("Préchauffage du modèle SBERT...")
    get_model()
    logger.info("Modèle SBERT prêt ✅ — premier appel sbert/hybrid/knn sera instantané")
    yield  # ← l'API tourne ici
    logger.info("Arrêt de l'API...")

app = FastAPI(
    title       = "Job Market API",
    description = "API de recherche et recommandation d'offres d'emploi",
    version     = "1.0.0",
    lifespan    = lifespan
)

app.include_router(jobs.router,            prefix="/offers",    tags=["Offres"])
app.include_router(recommendations.router, prefix="/recommend", tags=["Recommandations"])
app.include_router(stats.router,           prefix="/stats",     tags=["Statistiques"])

@app.get("/health")
def health():
    return {"status": "ok"}
