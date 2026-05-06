from fastapi import FastAPI
from services.api.src.routers import jobs,recommendations

app = FastAPI(
    title       = "Job Market API",
    description = "API de recherche et recommandation d'offres d'emploi",
    version     = "1.0.0",
)

# Enregistrer les routes
app.include_router(jobs.router, prefix="/offers", tags=["Offres"])
app.include_router(recommendations.router, prefix="/recommend", tags=["Recommandations"])

@app.get("/health")
def health():
    return {"status": "ok"}
