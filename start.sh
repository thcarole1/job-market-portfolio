#!/bin/bash
set -e  # arrête le script si une commande échoue

# ── Configuration du PYTHONPATH ───────────────
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "📂 PYTHONPATH configuré : $(pwd)"

echo "============================================"
echo "🚀 Démarrage de Job Market Portfolio"
echo "============================================"

# ── Étape 1 : Démarrage des services Docker ───
echo ""
echo "📦 Démarrage des services Docker..."
docker compose up -d mongodb elasticsearch postgresql pgadmin kibana
echo "⏳ Attente du démarrage d'Elasticsearch (30s)..."
sleep 30

# Vérification Elasticsearch
until curl -s http://localhost:9200 > /dev/null; do
    echo "⏳ Elasticsearch pas encore prêt, nouvelle tentative dans 5s..."
    sleep 5
done
echo "✅ Elasticsearch prêt"

# ── Étape 2 : Collecte des offres ─────────────
echo ""
echo "📥 Collecte des offres..."
python services/ingestion/src/main.py
echo "✅ Collecte terminée"

# ── Étape 3 : Entraînement du modèle ML ───────
echo ""
echo "🤖 Entraînement du modèle TF-IDF..."
python services/ml/src/main.py
echo "✅ Modèle entraîné"

# ── Étape 4 : Lancement de l'API ──────────────
echo ""
echo "🌐 Lancement de l'API FastAPI..."
python -m uvicorn services.api.src.main:app --port 8000 &
API_PID=$!
sleep 3

# Vérification API
until curl -s http://localhost:8000/health > /dev/null; do
    echo "⏳ API pas encore prête..."
    sleep 2
done
echo "✅ API prête sur http://localhost:8000"

# ── Étape 5 : Lancement du frontend ───────────
echo ""
echo "🖥️  Lancement du frontend Streamlit..."
echo "✅ Frontend disponible sur http://localhost:8501"
echo ""
echo "============================================"
echo "✅ Job Market Portfolio est prêt !"
echo "   API      → http://localhost:8000/docs"
echo "   Frontend → http://localhost:8501"
echo "   Kibana   → http://localhost:5601"
echo "   pgAdmin  → http://localhost:5050"
echo "============================================"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

streamlit run services/frontend/src/main.py

# Nettoyage à l'arrêt
trap "kill $API_PID; docker compose stop" EXIT
