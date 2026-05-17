"""
DAG Airflow — Pipeline d'ingestion nocturne (granulaire)
========================================================
Orchestre le pipeline de collecte et d'enrichissement des offres d'emploi
en 5 tâches séquentielles indépendantes.

Structure :
    t1 : collecte_france_travail        → collecte API + insertion offres_brutes
    t2 : normalisation                  → normalisation + insertion offres_normalisees
    t3 : calcul_embeddings_sbert        → calcul embeddings 768 dimensions
    t4 : indexation_elasticsearch       → indexation dense_vector KNN
    t5 : enrichissement_skills          → extraction SBERT zero-shot hard/soft skills

Planning :
    Production : tous les jours à 2h ("0 2 * * *")
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from services.ingestion.src.main import (
    run_collecte,
    run_normalisation,
    run_embeddings,
    run_indexation_es,
    run_enrich,
)

# ── Définition du DAG ────────────────────────────────────────────────────────
with DAG(
    dag_id="ingestion_nocturne",
    description="Pipeline ELT complet — collecte, normalisation, SBERT, ES, skills",
    start_date=datetime(2026, 5, 16),
    schedule="0 2 * * *",   # tous les jours à 2h (production)
    catchup=False,
    tags=["ingestion", "france-travail", "sbert"],
) as dag:

    # ── Tâche 1 : Collecte France Travail ─────────────────────────────────────
    t1 = PythonOperator(
        task_id="collecte_france_travail",
        python_callable=run_collecte,
    )

    # ── Tâche 2 : Normalisation ───────────────────────────────────────────────
    t2 = PythonOperator(
        task_id="normalisation",
        python_callable=run_normalisation,
    )

    # ── Tâche 3 : Calcul embeddings SBERT ────────────────────────────────────
    t3 = PythonOperator(
        task_id="calcul_embeddings_sbert",
        python_callable=run_embeddings,
    )

    # ── Tâche 4 : Indexation Elasticsearch ───────────────────────────────────
    t4 = PythonOperator(
        task_id="indexation_elasticsearch",
        python_callable=run_indexation_es,
    )

    # ── Tâche 5 : Enrichissement skills SBERT zero-shot ───────────────────────
    t5 = PythonOperator(
        task_id="enrichissement_skills",
        python_callable=run_enrich,
    )

    # ── Dépendances séquentielles ─────────────────────────────────────────────
    t1 >> t2 >> t3 >> t4 >> t5
