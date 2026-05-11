import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard — Marché de l'emploi")

# ── Fonctions de visualisation ────────────────────────
def bar_chart_sorted(data: list, title: str):
    """Affiche un bar chart horizontal trié par ordre décroissant."""
    if not data:
        st.info("Aucune donnée disponible")
        return
    df = pd.DataFrame(data).sort_values("count", ascending=True)
    fig = px.bar(
        df,
        x="count",
        y="label",
        orientation="h",
        title=title,
        color_discrete_sequence=["#4C78A8"]
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Nombre d'offres",
        height=400
    )
    st.plotly_chart(fig, width='stretch')


def line_chart_temporal(data: list, title: str):
    """Affiche un line chart pour l'évolution temporelle."""
    if not data:
        st.info("Aucune donnée disponible")
        return
    df = pd.DataFrame(data).sort_values("label")  # ordre chronologique
    fig = px.line(
        df,
        x="label",
        y="count",
        title=title,
        markers=True
    )
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Nombre d'offres",
        height=400
    )
    st.plotly_chart(fig, width='stretch')

# ── Fonctions cache ───────────────────────────────────

@st.cache_data(ttl=3600)
def get_rome_labels():
    try:
        r = requests.get(f"{API_URL}/offers/rome-labels")
        return ["Tous"] + sorted(r.json())
    except:
        return ["Tous"]

@st.cache_data(ttl=300)
def get_stats(rome_label=None, ville=None, periode=None):
    params = {}
    if rome_label and rome_label != "Tous":
        params["rome_label"] = rome_label
    if ville:
        params["ville"] = ville
    if periode:
        params["periode"] = periode
    r = requests.get(f"{API_URL}/stats/", params=params)
    return r.json()

# ── Filtres ───────────────────────────────────────────
st.subheader("🔎 Filtres")
col1, col2, col3 = st.columns(3)
with col1:
    rome_labels      = get_rome_labels()
    metier_selectionne = st.selectbox("Métier", rome_labels)
with col2:
    ville_filtre = st.text_input("Ville", placeholder="Ex: Paris")
with col3:
    periode_filtre = st.text_input("Période", placeholder="Ex: 2026-03")

st.markdown("---")

# ── Chargement stats ──────────────────────────────────
with st.spinner("Chargement des statistiques..."):
    stats = get_stats(
        rome_label=metier_selectionne,
        ville=ville_filtre or None,
        periode=periode_filtre or None
    )

# ── KPIs ──────────────────────────────────────────────
st.subheader("📈 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total offres", stats["total"])

par_contrat = {r["label"]: r["count"] for r in stats["par_contrat"]}
col2.metric("CDI",  par_contrat.get("CDI", 0))
col3.metric("CDD",  par_contrat.get("CDD", 0))

alternance = {r["label"]: r["count"] for r in stats["alternance"]}
col4.metric("Alternance", alternance.get("Alternance", 0))

st.markdown("---")

# ── Graphiques ligne 1 ────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    bar_chart_sorted(stats["par_contrat"], "📋 Répartition par type de contrat")

with col2:
    bar_chart_sorted(stats["top_villes"], "🏙️ Top 10 villes")

# ── Graphiques ligne 2 ────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    bar_chart_sorted(stats["top_secteurs"], "🏭 Top 10 secteurs d'activité")

with col2:
    bar_chart_sorted(stats["par_experience"], "📅 Répartition par expérience")

# ── Graphiques ligne 3 ────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    bar_chart_sorted(stats["top_metiers"], "💼 Top 10 métiers")

with col2:
    line_chart_temporal(stats["evolution"], "📆 Évolution mensuelle des offres")
