import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Marché de l'emploi — Vue d'ensemble")
st.caption("Données issues de France Travail — actualisées quotidiennement")

# ── Palette cohérente ─────────────────────────────────────────────────────────
BLUE   = "#4C78A8"
GREEN  = "#54A24B"
ORANGE = "#F58518"
RED    = "#E45756"
PURPLE = "#B279A2"
TEAL   = "#4DBBD5"
COLORS = [BLUE, GREEN, ORANGE, RED, PURPLE, TEAL,
          "#EDC948", "#FF9DA7", "#9D755D", "#BAB0AC"]

# ── Helpers graphiques ────────────────────────────────────────────────────────

def bar_h(data: list, title: str, color: str = BLUE, height: int = 380) -> go.Figure:
    """Bar chart horizontal trié."""
    if not data:
        return None
    df = pd.DataFrame(data).sort_values("count", ascending=True)
    fig = px.bar(df, x="count", y="label", orientation="h",
                 title=title, color_discrete_sequence=[color])
    fig.update_layout(yaxis_title="", xaxis_title="Offres",
                      height=height, margin=dict(l=0, r=10, t=40, b=0))
    return fig


def bar_v(data: list, title: str, color: str = BLUE, height: int = 340) -> go.Figure:
    """Bar chart vertical."""
    if not data:
        return None
    df = pd.DataFrame(data).sort_values("count", ascending=False)
    fig = px.bar(df, x="label", y="count", title=title,
                 color_discrete_sequence=[color])
    fig.update_layout(xaxis_title="", yaxis_title="Offres",
                      height=height, margin=dict(l=0, r=10, t=40, b=60),
                      xaxis_tickangle=-30)
    return fig


def pie(data: list, title: str, height: int = 340) -> go.Figure:
    """Pie chart."""
    if not data:
        return None
    df = pd.DataFrame(data)
    fig = px.pie(df, names="label", values="count", title=title,
                 color_discrete_sequence=COLORS, hole=0.35)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=40, b=0),
                      legend=dict(orientation="v", x=1, y=0.5))
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def line_trend(data: list, title: str, height: int = 340) -> go.Figure:
    """Line chart avec droite de tendance."""
    if not data:
        return None
    df = pd.DataFrame(data).sort_values("label")
    fig = go.Figure()

    # Ligne principale
    fig.add_trace(go.Scatter(
        x=df["label"], y=df["count"],
        mode="lines+markers",
        name="Offres publiées",
        line=dict(color=BLUE, width=2),
        marker=dict(size=6),
    ))

    # Tendance linéaire simple
    if len(df) >= 3:
        import numpy as np
        x_num = list(range(len(df)))
        z     = np.polyfit(x_num, df["count"], 1)
        p     = np.poly1d(z)
        trend = p(x_num)
        direction = "↗ Tendance haussière" if z[0] > 0 else "↘ Tendance baissière"
        fig.add_trace(go.Scatter(
            x=df["label"], y=trend,
            mode="lines",
            name=direction,
            line=dict(color=ORANGE, width=2, dash="dash"),
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Mois",
        yaxis_title="Offres",
        height=height,
        margin=dict(l=0, r=10, t=40, b=40),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def show(fig, key=None):
    """Affiche un graphique ou un message si données absentes."""
    if fig:
        st.plotly_chart(fig, use_container_width=True, key=key)
    else:
        st.info("Aucune donnée disponible")


# ── Cache ─────────────────────────────────────────────────────────────────────

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


# ── Filtres ───────────────────────────────────────────────────────────────────
with st.expander("🔎 Filtres", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        rome_labels        = get_rome_labels()
        metier_selectionne = st.selectbox("🎯 Métier", rome_labels)
    with col2:
        ville_filtre = st.text_input("📍 Ville", placeholder="Ex: Paris, Lyon...")
    with col3:
        mois_options   = ["Tous"] + [f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 6)]
        periode_filtre = st.selectbox("📅 Période", mois_options)

st.markdown("---")

# ── Chargement ────────────────────────────────────────────────────────────────
with st.spinner("Chargement des statistiques..."):
    stats = get_stats(
        rome_label=metier_selectionne if metier_selectionne != "Tous" else None,
        ville=ville_filtre or None,
        periode=None if periode_filtre == "Tous" else periode_filtre,
    )

# ── NIVEAU 1 : KPIs ───────────────────────────────────────────────────────────
st.subheader("📈 Indicateurs clés")

par_contrat  = {r["code"]: r["count"] for r in stats["par_contrat"]}
alternance   = {r["label"]: r["count"] for r in stats["alternance"]}
total        = stats["total"]

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("📋 Total offres",    f"{total:,}".replace(",", " "))
col2.metric("💼 CDI",             f"{par_contrat.get('CDI', 0):,}".replace(",", " "),
            f"{par_contrat.get('CDI', 0)/total*100:.0f}%" if total else "")
col3.metric("📄 CDD",             f"{par_contrat.get('CDD', 0):,}".replace(",", " "),
            f"{par_contrat.get('CDD', 0)/total*100:.0f}%" if total else "")
col4.metric("🔄 Intérim",         f"{par_contrat.get('MIS', 0):,}".replace(",", " "),
            f"{par_contrat.get('MIS', 0)/total*100:.0f}%" if total else "")
col5.metric("🎓 Alternance",      f"{alternance.get('Alternance', 0):,}".replace(",", " "))
col6.metric("💰 Salaire affiché", f"{stats.get('taux_salaire', 0)}%",
            "des offres")

st.markdown("---")

# ── NIVEAU 1 : Évolution temporelle ──────────────────────────────────────────
st.subheader("📆 Évolution des publications")
show(line_trend(stats["evolution"], "Publications mensuelles d'offres"), key="evolution")

st.markdown("---")

# ── NIVEAU 2 : Skills — valeur ajoutée ML ────────────────────────────────────
st.subheader("🧠 Compétences demandées — Analyse ML")
st.caption("Extraction automatique par modèle SBERT zero-shot sur l'ensemble des offres")

col1, col2 = st.columns(2)
with col1:
    show(bar_h(
        stats.get("top_competences", []),
        "🛠️ Top 20 compétences techniques (hard skills)",
        color=BLUE, height=500
    ), key="hard_skills")

with col2:
    # Fusion soft explicites + implicites pour un graphique unique
    soft_exp = stats.get("top_soft_explicites", [])
    soft_imp = stats.get("top_soft_implicites", [])

    # Marquer la source
    for s in soft_exp:
        s["source"] = "Explicite"
    for s in soft_imp:
        s["source"] = "Implicite"

    soft_all = sorted(soft_exp + soft_imp, key=lambda x: x["count"], reverse=True)[:15]

    if soft_all:
        df_soft = pd.DataFrame(soft_all).sort_values("count", ascending=True)
        fig_soft = px.bar(
            df_soft, x="count", y="label", orientation="h",
            color="source",
            color_discrete_map={"Explicite": GREEN, "Implicite": TEAL},
            title="🤝 Top 15 soft skills demandés",
        )
        fig_soft.update_layout(
            yaxis_title="", xaxis_title="Offres",
            height=500, margin=dict(l=0, r=10, t=40, b=0),
            legend=dict(title="Type", orientation="h", y=-0.15),
        )
        show(fig_soft, key="soft_skills")
    else:
        st.info("Soft skills en cours d'extraction — relancer après le batch nocturne.")

st.markdown("---")

# ── NIVEAU 3 : Données marché ─────────────────────────────────────────────────
st.subheader("🗺️ Données marché")

col1, col2 = st.columns(2)
with col1:
    show(bar_h(stats["top_villes"],   "🏙️ Top 10 villes",     color=BLUE),   key="villes")
with col2:
    show(pie(stats["par_contrat"][:6], "📋 Types de contrat"), key="contrats")

col1, col2 = st.columns(2)
with col1:
    show(bar_h(stats["par_experience"], "📅 Niveau d'expérience requis", color=ORANGE), key="experience")
with col2:
    show(bar_h(stats["top_secteurs"],   "🏭 Top 10 secteurs d'activité", color=PURPLE), key="secteurs")

col1, col2 = st.columns(2)
with col1:
    show(bar_h(stats["top_metiers"], "💼 Top 10 métiers", color=TEAL), key="metiers")
with col2:
    # Alternance : donut simple
    show(pie(stats["alternance"], "🎓 Alternance vs CDI/CDD"), key="alternance")

st.markdown("---")
st.caption(f"📊 {stats.get('avec_skills', 0):,} offres analysées par ML sur {total:,} au total ({stats.get('taux_skills', 0)}% du corpus)".replace(",", " "))
