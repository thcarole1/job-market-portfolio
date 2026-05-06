import streamlit as st

st.set_page_config(
    page_title="Job Market Portfolio",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Market Portfolio")
st.markdown("---")

st.markdown("""
### Bienvenue sur votre tableau de bord du marché de l'emploi Data

Naviguez via le menu à gauche :

- 📊 **Dashboard** — Statistiques du marché
- 🔍 **Recherche** — Recommandation d'offres par profil
- 📄 **Détail offre** — Consulter une offre en détail
""")

# Métriques rapides
st.markdown("---")
st.subheader("Vue d'ensemble")

col1, col2, col3 = st.columns(3)

API_URL = "http://localhost:8000"

import requests
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        col1.metric("Statut API", "✅ En ligne")
    else:
        col1.metric("Statut API", "❌ Hors ligne")
except:
    col1.metric("Statut API", "❌ Hors ligne")
