"""
DAG Airflow — Pipeline d'ingestion nocturne
===========================================
Orchestre le pipeline de collecte et d'enrichissement des offres d'emploi.

Structure :
    t1 : collecte_et_ingestion    → collecte France Travail + normalisation + indexation ES
    t2 : enrichissement_skills    → extraction SBERT zero-shot hard/soft skills

Planning :
    Test       : toutes les heures  ("0 * * * *")
    Production : tous les jours à 2h ("0 2 * * *")
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from services.ingestion.src.main import run_ingestion, run_enrich

# ── Définition du DAG ────────────────────────────────────────────────────────
with DAG(
    dag_id="ingestion_nocturne",
    description="Collecte France Travail + normalisation + enrichissement SBERT",
    start_date=datetime(2026, 5, 16),
    schedule="0 2 * * *",   # ← tous les jours à 2h (production)
    catchup=False,           # ne rattrape pas les exécutions manquées passées
    tags=["ingestion", "france-travail", "sbert"],
) as dag:

    # ── Tâche 1 : collecte + normalisation + indexation ───────────────────────
    t1 = PythonOperator(
        task_id="collecte_et_ingestion",
        python_callable=run_ingestion,
    )

    # ── Tâche 2 : enrichissement skills SBERT zero-shot ───────────────────────
    t2 = PythonOperator(
        task_id="enrichissement_skills",
        python_callable=run_enrich,
    )

    # ── Dépendance : t2 attend que t1 réussisse ───────────────────────────────
    t1 >> t2
