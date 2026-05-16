# 🎯 Job Market Portfolio

> Plateforme de collecte, analyse et recommandation d'offres d'emploi — projet Data Engineer

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.0-green?logo=mongodb)](https://mongodb.com)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.17-yellow?logo=elasticsearch)](https://elastic.co)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![CI](https://github.com/thcarole1/job-market-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/thcarole1/job-market-portfolio/actions/workflows/ci.yml)
[![Airflow](https://img.shields.io/badge/Airflow-2.9.1-017CEE?logo=apacheairflow)](https://airflow.apache.org)

---

## 📋 Table des matières

- [Présentation](#-présentation)
- [Architecture](#-architecture)
- [Stack technique](#-stack-technique)
- [Structure du projet](#-structure-du-projet)
- [Démarrage rapide](#-démarrage-rapide)
- [Variables d'environnement](#-variables-denvironnement)
- [Pipeline ELT](#-pipeline-elt)
- [Modèles ML](#-modèles-ml)
- [API](#-api)
- [Frontend](#-frontend)
- [Tests](#-tests)
- [Scripts utilitaires](#-scripts-utilitaires)
- [Runbook](#-runbook)

---

## 🎯 Présentation

**Job Market Portfolio** est une application end-to-end de Data Engineering qui collecte les offres d'emploi via l'API France Travail, les stocke et indexe, puis propose un moteur de recommandation basé sur le profil ou le CV d'un utilisateur.

### Fonctionnalités principales

- **Collecte incrémentale** — collecte nocturne automatisée des nouvelles offres uniquement, filtrées par date et IDs existants
- **Pipeline ELT complet** — collecte → normalisation → embedding SBERT → MongoDB → Elasticsearch
- **4 modèles de recommandation** — TF-IDF, SBERT, Hybrid (5 critères pondérés), KNN (HNSW Elasticsearch)
- **Extraction de skills** — détection automatique des hard skills et soft skills par SBERT zero-shot sur 42 000+ offres
- **Analyse CV/offre** — gap analysis entre le profil du candidat et les offres recommandées avec recommandations personnalisées
- **Dashboard marché** — statistiques agrégées avec visualisation des compétences techniques et soft skills les plus demandés
- **API REST** — FastAPI avec endpoints de recommandation, statistiques et consultation des offres
- **Déploiement Docker** — 7 services conteneurisés, reproductible sur toute machine

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Streamlit                        │
│              Dashboard │ Recherche │ Détail offre               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────────┐
│                         API FastAPI                              │
│         /offers  │  /recommend  │  /recommend/cv  │  /stats     │
└──────┬───────────────────┬──────────────────────────────────────┘
       │                   │
┌──────▼──────┐   ┌────────▼────────┐
│   MongoDB   │   │ Elasticsearch   │
│  (source    │   │  (recherche +   │
│  de vérité) │   │   embeddings)   │
└──────▲──────┘   └────────▲────────┘
       │                   │
┌──────┴───────────────────┴──────────────────────────────────────┐
│                     Pipeline ELT (Ingestion)                     │
│  France Travail API → Normalisation → SBERT → Enrichissement    │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de données

```
Nuit :
  API France Travail
       │ collecte incrémentale (nouvelles offres uniquement)
       ▼
  offres_brutes (MongoDB)
       │ normalisation + embedding SBERT (768 dims)
       ▼
  offres_normalisees (MongoDB)  ──────►  Index offres (Elasticsearch)
       │ enrichissement skills SBERT zero-shot
       ▼
  skills_extraits { hard_skills, soft_explicites, soft_implicites }

Jour (à la demande) :
  CV PDF → CVParser → CVStructurer → hard_skills + soft_skills
       │ embedding global
       ▼
  KNN / Cosine similarity (Elasticsearch)
       │ top N offres similaires
       ▼
  HybridScorer (SBERT 50% + compétences 30% + expérience 10% + localisation 5% + formation 5%)
       │ compute_gap (maîtrisé / manquant / recommandations)
       ▼
  Résultats enrichis → Streamlit
```

---

## 🛠️ Stack technique

| Catégorie | Technologie | Usage |
|---|---|---|
| Langage | Python 3.12 | Backend, ML, scripts |
| API | FastAPI | REST API, lifespan SBERT warmup |
| Frontend | Streamlit | Dashboard, recherche, analyse CV |
| Base NoSQL | MongoDB 8.0 | Source de vérité, offres brutes et normalisées |
| Moteur de recherche | Elasticsearch 8.17 | Index dense_vector 768 dims, KNN HNSW |
| Base relationnelle | PostgreSQL 16 | Données structurées (suivi candidatures) |
| ML — Embeddings | SBERT paraphrase-multilingual-mpnet-base-v2 | Vectorisation offres et CV |
| ML — Recherche | TF-IDF, Cosine similarity, KNN | 4 modèles de recommandation |
| Conteneurisation | Docker + Docker Compose | 7 services, reproductibilité |
| Tests | pytest | 41+ tests unitaires et d'intégration |
| Orchestration | Airflow 2.9.1 | DAG ingestion_nocturne — collecte quotidienne à 2h |
| CI/CD | GitHub Actions | Tests unitaires automatiques sur push et PR |
| Versioning | Git + GitHub | Workflow `main ← develop ← feat/*` |

---

## 📁 Structure du projet

```
job-market-portfolio/
├── config/
│   └── settings.py                     # Pydantic BaseSettings — variables d'env
│
├── scripts/
│   ├── reset_db.py                     # Reset MongoDB + ES (--es-only)
│   ├── reindex_elasticsearch.py        # Réindexe ES depuis MongoDB
│   ├── enrich_competences.py           # Enrichit offres avec competences_detectees
│   ├── enrich_skills.py                # Batch SBERT zero-shot (hard + soft skills)
│   └── enrich_coordinates.py          # Géocodage GPS via API Géo gouv.fr
│
├── services/
│   ├── ingestion/src/
│   │   ├── collectors/
│   │   │   └── france_travail.py       # Collecte incrémentale multi-ROME
│   │   ├── loaders/
│   │   │   ├── mongo_loader.py         # MongoLoader — upsert offres brutes/normalisées
│   │   │   └── elastic_loader.py      # ElasticLoader — index dense_vector
│   │   ├── utils/
│   │   │   └── normalizer.py          # normalize_france_travail() + competences_detectees
│   │   └── main.py                    # Pipeline ELT complet
│   │
│   ├── ml/src/
│   │   ├── constants.py               # COMPETENCES_CONNUES (229), SOFT_SKILLS_REFERENCES (10 × 20 phrases), VILLES_CONNUES, etc.
│
│   │   ├── encoder.py                 # Singleton SBERT
│   │   ├── features.py                # build_offer_text()
│   │   ├── cv_parser.py               # CVParser — PDF → texte
│   │   ├── cv_structurer.py           # CVStructurer — hard_skills + soft_skills + expérience
│   │   ├── skills_extractor.py        # SkillsExtractor — SBERT zero-shot + compute_gap
│   │   ├── hybrid_scorer.py           # HybridScorer — 5 critères pondérés + Haversine
│   │   ├── predict.py                 # TF-IDF
│   │   ├── predict_sbert.py           # SBERT cosine
│   │   ├── predict_hybrid.py          # Hybrid (SBERT + critères)
│   │   └── predict_knn.py             # KNN Elasticsearch HNSW
│   │
│   ├── api/src/
│   │   ├── main.py                    # FastAPI app + lifespan SBERT warmup
│   │   └── routers/
│   │       ├── jobs.py                # GET /offers/, GET /offers/{id}
│   │       ├── recommendations.py     # POST /recommend/, POST /recommend/cv
│   │       └── stats.py               # GET /stats/ — agrégations MongoDB
│   │
│   └── frontend/src/
│       ├── main.py                    # Streamlit — page d'accueil
│       └── pages/
│           ├── dashboard.py           # Stats marché + soft skills ML
│           ├── search.py              # Recherche texte libre + upload CV
│           └── offer_detail.py        # Détail offre par ID
│
├── storage/
│   ├── elasticsearch/
│   │   └── mappings.json              # Mapping ES dense_vector 768 dims
│   └── mongodb/
│       └── init.js                    # Initialisation MongoDB (index, collections)
│
├── orchestration/
│   └── dags/
│       ├── ingestion_dag.py           # DAG Airflow — collecte nocturne quotidienne
│       └── Dockerfile                 # Image Airflow custom avec dépendances projet
│
├── notebooks/
│   ├── test_skills_extractor.ipynb    # Validation extraction skills
│   ├── test_pipeline_validation.ipynb # Validation post-batch 40k offres
│   └── test_api_skills.ipynb          # Tests API skills_gap
│
├── tests/
│   ├── api/                           # test_jobs, test_recommendations, test_stats
│   ├── ingestion/                     # test_normalizer
│   └── ml/                            # test_cv_structurer, test_hybrid_scorer, test_skills_extractor
│
├── docker-compose.yml                 # 10 services (dont 3 Airflow)
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## 🚀 Démarrage rapide

### Prérequis

- Docker + Docker Compose
- Python 3.12 (pour le développement local)
- Clés API France Travail ([obtenir ici](https://francetravail.io/data/api))

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/thcarole1/job-market-portfolio.git
cd job-market-portfolio

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 3. Lancer tous les services
docker compose up -d

# 4. Vérifier que tout tourne
docker compose ps
```

### Accès aux services

| Service | URL | Description |
|---|---|---|
| Frontend Streamlit | http://localhost:8501 | Interface utilisateur |
| API FastAPI | http://localhost:8000 | REST API + Swagger UI |
| API Docs | http://localhost:8000/docs | Documentation interactive |
| Airflow | http://localhost:8080 | Orchestration — DAG ingestion_nocturne |
| Kibana | http://localhost:5601 | Interface Elasticsearch |
| PgAdmin | http://localhost:5050 | Interface PostgreSQL |

### Premier lancement — collecte des données

```bash
# Collecte initiale (toutes les offres)
docker compose run --rm ingestion

# Ou en local
PYTHONPATH=. python services/ingestion/src/main.py
```

---

## ⚙️ Variables d'environnement

Copier `.env.example` en `.env` et remplir les valeurs :

```bash
# MongoDB
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=your_username
MONGO_INITDB_ROOT_PASSWORD=your_password

# Elasticsearch
ELASTIC_HOST=elasticsearch
ELASTIC_PORT=9200
ELASTICSEARCH_INDEX=offres

# PostgreSQL
POSTGRES_HOST=postgresql
POSTGRES_PORT=5432
POSTGRES_DB=job_market
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# API France Travail (obligatoire pour la collecte)
FRANCETRAVAIL_CLIENT_ID=your_client_id
FRANCETRAVAIL_CLIENT_SECRET=your_client_secret

# Ports exposés
API_PORT=8000
FRONTEND_PORT=8501

# Environnement
ENVIRONMENT=dev
LOG_LEVEL=INFO

# Airflow
AIRFLOW_SECRET_KEY=your_secret_key_here  # générer avec : python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔄 Pipeline ELT

Le pipeline s'exécute via `services/ingestion/src/main.py` et suit 6 étapes :

```
1. Connexion MongoDB → récupération des IDs existants + date dernière offre
2. Collecte France Travail API (incrémentale — nouvelles offres uniquement)
3. Insertion offres brutes → MongoDB (offres_brutes)
4. Normalisation → encode SBERT (768 dims) → MongoDB (offres_normalisees)
5. Indexation → Elasticsearch (dense_vector)
6. Enrichissement skills → SBERT zero-shot (hard + soft skills)
```

### Codes ROME collectés

37 codes ROME couvrant : Data & IA, Informatique & SI, Management, Finance, Marketing, RH, Santé, BTP, Logistique, Restauration.

### Enrichissement skills (SBERT zero-shot)

```bash
# Enrichir uniquement les nouvelles offres
PYTHONPATH=. python scripts/enrich_skills.py

# Options
--force          # Re-traite toutes les offres
--limit 100      # Test sur N offres
--dry-run        # Sans écriture MongoDB
--threshold 0.75 # Seuil similarité cosine (défaut)
```

**Résultat stocké dans MongoDB :**
```json
{
  "skills_extraits": {
    "hard_skills": ["Python", "Docker", "Elasticsearch"],
    "soft_explicites": ["Autonomie", "Rigueur", "Travail en équipe"],
    "soft_implicites": ["Fiabilité"],
    "methode": "sbert_zero_shot",
    "seuil": 0.75,
    "version": "1.0"
  }
}
```

---

## 🤖 Modèles ML

### 4 modèles de recommandation

| Modèle | Approche | Latence | Détail disponible |
|---|---|---|---|
| TF-IDF | Fréquence de mots | ~1s | ❌ |
| SBERT | Similarité cosine sémantique | ~2s | ❌ |
| Hybrid | 5 critères pondérés | ~2–12s | ✅ |
| KNN | HNSW Elasticsearch + scoring | ~2s | ✅ |

### HybridScorer — pondérations

```python
POIDS = {
    "sbert":        0.50,  # Similarité sémantique globale
    "competences":  0.30,  # Hard skills (70%) + Soft skills (30%)
    "experience":   0.10,  # Années d'expérience
    "localisation": 0.05,  # Distance Haversine (km)
    "formation":    0.05,  # Niveau de diplôme
}
```

### Extraction de skills CV

Le `CVStructurer` extrait automatiquement depuis un PDF :
- **Hard skills** — détection par lexique (229 compétences connues)
- **Soft skills** — détection SBERT zero-shot (10 skills × 20 phrases-référence)
- Années d'expérience, localisation, formation, langues

### Gap analysis CV/offre

```python
gap = extractor.compute_gap(cv_skills, offer_result)
# → {
#     "taux_match": 65.0,
#     "maitrise":   ["python", "docker"],
#     "manquants":  ["autonomie", "rigueur"],
#     "bonus":      ["kubernetes"],
#     "recommandations": ["..."]
# }
```

---

## 🌐 API

Documentation interactive disponible sur `http://localhost:8000/docs`

### Endpoints principaux

```
GET  /offers/                    # Liste des offres avec filtres ES
GET  /offers/{id}                # Détail d'une offre
GET  /offers/rome-labels         # Labels ROME disponibles

POST /recommend/                 # Recommandation par texte libre
POST /recommend/cv               # Recommandation par CV PDF (+ skills_gap)

GET  /stats/                     # Statistiques marché agrégées
```

### Exemple — recommandation par CV

```bash
curl -X POST "http://localhost:8000/recommend/cv?model=knn&top_n=10&show_detail=true" \
     -F "file=@mon_cv.pdf"
```

**Réponse :**
```json
[
  {
    "title": "Data Engineer Python",
    "score": 0.821,
    "skills_gap": {
      "taux_match": 65.0,
      "maitrise": ["python", "docker"],
      "manquants": ["autonomie", "rigueur"],
      "recommandations": ["..."]
    },
    "detail": {
      "sbert": 0.84,
      "competences": {"score": 0.70, "hard": {...}, "soft": {...}},
      "experience": {"score": 1.0},
      "localisation": {"score": 1.0, "distance_km": 3.5},
      "formation": {"score": 1.0}
    }
  }
]
```

---

## 🖥️ Frontend

L'interface Streamlit propose 3 pages :

### 📊 Dashboard
- KPIs marché (total offres, CDI, alternance, transparence salariale)
- Évolution mensuelle avec droite de tendance
- **Top hard skills et soft skills** extraits par ML (différenciant)
- Répartition contrats, villes, secteurs, expérience, métiers
- Filtres : métier, ville, période

### 🔍 Recherche
- **Onglet texte libre** — recherche par mots-clés avec filtres
- **Onglet CV PDF** — upload → extraction automatique → recommandations + analyse de compatibilité
- 4 modèles sélectionnables
- Analyse de compatibilité : jauge de match skills, pills maîtrisés/manquants, recommandations personnalisées

### 📄 Détail offre
- Consultation d'une offre par référence

---

## 🧪 Tests

```bash
# Lancer tous les tests
PYTHONPATH=. pytest tests/ -v

# Tests unitaires uniquement (sans modèle SBERT)
PYTHONPATH=. pytest tests/ -m "not integration" -v

# Tests d'intégration (nécessitent le modèle SBERT)
PYTHONPATH=. pytest tests/ -m "integration" -v

# Par module
PYTHONPATH=. pytest tests/api/ -v
PYTHONPATH=. pytest tests/ml/ -v
PYTHONPATH=. pytest tests/ingestion/ -v
```

**Couverture actuelle :** 41+ tests — API, ingestion, ML (normalizer, CV structurer, hybrid scorer, skills extractor)

---

## 🔧 Scripts utilitaires

```bash
# Reset complet MongoDB + Elasticsearch
PYTHONPATH=. python scripts/reset_db.py

# Reset Elasticsearch uniquement
PYTHONPATH=. python scripts/reset_db.py --es-only

# Réindexer ES depuis MongoDB
PYTHONPATH=. python scripts/reindex_elasticsearch.py

# Enrichir les compétences détectées (lexique)
PYTHONPATH=. python scripts/enrich_competences.py

# Enrichir les skills SBERT zero-shot (nouvelles offres uniquement)
PYTHONPATH=. python scripts/enrich_skills.py

# Enrichir les coordonnées GPS via API Géo
PYTHONPATH=. python scripts/enrich_coordinates.py --limit 100 --dry-run
```

---

## 📖 Runbook

### Démarrage complet

```bash
docker compose up -d
```

### Rebuild d'un service

```bash
docker compose build api && docker compose up -d api
docker compose build frontend && docker compose up -d frontend
```

### Collecte manuelle

```bash
PYTHONPATH=. python services/ingestion/src/main.py
```

### Airflow

```bash
# Initialiser Airflow (première fois uniquement)
docker compose up airflow-init

# Lancer le scheduler et le webserver
docker compose up -d airflow-scheduler airflow-webserver

# Voir les DAGs disponibles
docker exec airflow-scheduler airflow dags list

# Activer/désactiver le DAG
docker exec airflow-scheduler airflow dags unpause ingestion_nocturne
docker exec airflow-scheduler airflow dags pause ingestion_nocturne

# Interface web
open http://localhost:8080  # admin / admin
```

### Lancement Streamlit en local (développement)

```bash
cd services/frontend/src
PYTHONPATH=../../.. streamlit run main.py
```

### Workflow Git

```
main ← develop ← feat/*
                  docs/*
                  fix/*
```

**Conventions de commits :**
```
feat:  nouvelle fonctionnalité
fix:   correction de bug
chore: maintenance, dépendances
docs:  documentation
```

---

## 🗺️ Roadmap

- [x] Collecte API France Travail multi-ROME
- [x] Pipeline ELT complet avec SBERT
- [x] 4 modèles de recommandation
- [x] Extraction SBERT zero-shot hard/soft skills
- [x] Gap analysis CV/offre avec recommandations
- [x] API FastAPI + Frontend Streamlit
- [x] Conteneurisation Docker complète
- [x] Dashboard marché avec soft skills ML
- [x] Airflow — orchestration nocturne automatisée (DAG quotidien à 2h)
- [ ] Monitoring Prometheus + Grafana
- [x] Pipeline CI/CD GitHub Actions (tests unitaires sur push et PR)
- [ ] Reverse proxy Nginx (sécurité)
- [ ] Géocodage GPS (API Géo gouv.fr)
- [ ] Génération CV/LM personnalisés

---

## 📄 Licence

Projet réalisé dans le cadre d'une formation Data Engineer — Liora (2025-2026).
