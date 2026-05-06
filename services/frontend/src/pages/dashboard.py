import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard — Marché de l'emploi Data")

# Chargement des données
@st.cache_data(ttl=300)
def load_offers():
    all_offers = []
    skip = 0
    limit = 200
    while True:
        r = requests.get(f"{API_URL}/offers/", params={"limit": limit, "skip": skip})
        data = r.json()
        if not data:
            break
        all_offers.extend(data)
        if len(data) < limit:
            break
        skip += limit
    return pd.DataFrame(all_offers)

with st.spinner("Chargement des offres..."):
    df = load_offers()

st.success(f"{len(df)} offres chargées")

# Après le chargement des données
st.markdown("---")
st.subheader("Filtres")

metiers = ["Tous"] + sorted(df["rome_label"].dropna().unique().tolist())
metier_selectionne = st.selectbox("Filtrer par métier", metiers)

if metier_selectionne != "Tous":
    df = df[df["rome_label"] == metier_selectionne]

st.success(f"{len(df)} offres affichées")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total offres", len(df))
col2.metric("CDI", len(df[df["contract_type"] == "CDI"]))
col3.metric("CDD", len(df[df["contract_type"] == "CDD"]))
col4.metric("Villes uniques", df["workplace_label"].nunique())

st.markdown("---")

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("Répartition par type de contrat")
    contract_counts = df["contract_type"].value_counts()
    st.bar_chart(contract_counts)

with col2:
    st.subheader("Top 10 villes")
    city_counts = df["workplace_label"].value_counts().head(10)
    st.bar_chart(city_counts)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 secteurs d'activité")
    sector_counts = df["sector_activity_label"].dropna().value_counts().head(10)
    st.bar_chart(sector_counts)

with col2:
    st.subheader("Répartition par expérience requise")
    exp_map = {"D": "Débutant", "S": "Souhaitée", "E": "Exigée"}
    exp_counts = df["required_experience"].map(exp_map).value_counts()
    st.bar_chart(exp_counts)
