import time
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Recherche", page_icon="🔍", layout="wide")
st.title("🔍 Recherche d'offres par profil")

st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        background-color: #f0f4ff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .skills-match   { background:#d4edda; color:#155724; padding:3px 10px; border-radius:12px; margin:3px; display:inline-block; font-size:0.85em; font-weight:500; }
    .skills-missing { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:12px; margin:3px; display:inline-block; font-size:0.85em; font-weight:500; }
    .skills-bonus   { background:#d1ecf1; color:#0c5460; padding:3px 10px; border-radius:12px; margin:3px; display:inline-block; font-size:0.85em; font-weight:500; }
    .match-badge    { font-size:1.1em; font-weight:bold; padding:4px 12px; border-radius:16px; }
    .match-high     { background:#d4edda; color:#155724; }
    .match-mid      { background:#fff3cd; color:#856404; }
    .match-low      { background:#f8d7da; color:#721c24; }
    .score-card     { background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px; padding:12px 16px; margin:6px 0; }
    .score-label    { font-size:0.82em; color:#6c757d; margin-bottom:2px; }
    .score-value    { font-size:1.4em; font-weight:700; color:#212529; }
    .score-bar-bg   { background:#e9ecef; border-radius:4px; height:8px; margin-top:6px; }
    .score-bar-fill { height:8px; border-radius:4px; }
    .compat-section { border-left:3px solid #4e73df; padding-left:12px; margin:10px 0; }
    .offre-header   { font-size:1.05em; font-weight:600; color:#1a1a2e; margin-bottom:4px; }
    .offre-sub      { font-size:0.88em; color:#6c757d; }
    .info-chip      { background:#f0f4ff; border:1px solid #c5d0f5; color:#2c3e7a; padding:3px 10px; border-radius:10px; margin:2px; display:inline-block; font-size:0.84em; }
    .compat-global  { border-radius:10px; padding:14px 18px; margin:10px 0; }
    .rec-box        { background:#fff8e1; border-left:4px solid #ffc107; border-radius:6px; padding:10px 14px; margin:6px 0; font-size:0.9em; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_rome_labels():
    try:
        r = requests.get(f"{API_URL}/offers/rome-labels")
        return sorted(r.json())
    except:
        return []


def _match_badge(taux: float) -> str:
    if taux >= 70:
        css, emoji = "match-high", "🟢"
    elif taux >= 40:
        css, emoji = "match-mid", "🟡"
    else:
        css, emoji = "match-low", "🔴"
    return f'<span class="match-badge {css}">{emoji} {taux:.0f}% skills</span>'


def _pills(items: list, css_class: str) -> str:
    if not items:
        return "<em style='color:#999'>aucun</em>"
    return " ".join(f'<span class="{css_class}">{s}</span>' for s in items)


def _score_card(label: str, value: float, emoji: str = "") -> str:
    pct   = int(value * 100)
    color = "#28a745" if value >= 0.8 else "#ffc107" if value >= 0.5 else "#dc3545"
    return f"""
    <div class="score-card">
        <div class="score-label">{emoji} {label}</div>
        <div class="score-value">{value:.2f}</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
    </div>"""


def _compat_global_html(score: float) -> str:
    pct   = int(score * 100)
    color = "#28a745" if score >= 0.8 else "#ffc107" if score >= 0.5 else "#dc3545"
    bg    = "#f0fff4" if score >= 0.8 else "#fffbf0" if score >= 0.5 else "#fff5f5"
    label = "Excellent" if score >= 0.8 else "Bon" if score >= 0.5 else "Partiel"
    return f"""
    <div class="compat-global" style="background:{bg}; border:1.5px solid {color};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:1em; color:#444;">🏆 Score de compatibilité global</span>
            <span style="font-size:1.5em; font-weight:700; color:{color};">{score:.3f} <span style="font-size:0.55em; color:#888;">/ 1.000</span></span>
        </div>
        <div class="score-bar-bg" style="margin-top:8px;">
            <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
        <div style="text-align:right; font-size:0.8em; color:{color}; margin-top:4px;">{label}</div>
    </div>"""


def _display_skills_gap(gap: dict) -> None:
    taux      = gap.get("taux_match", 0)
    maitrise  = gap.get("maitrise", [])
    manquants = gap.get("manquants", [])
    bonus     = gap.get("bonus", [])
    recs      = gap.get("recommandations", [])

    # Jauge + badge
    col_g, col_b = st.columns([2, 1])
    with col_g:
        st.progress(int(taux) / 100)
    with col_b:
        st.markdown(_match_badge(taux), unsafe_allow_html=True)

    st.caption(f"{len(maitrise)} skill(s) maîtrisé(s) sur {len(maitrise) + len(manquants)} requis par l'offre")

    # Pills
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("✅ **Maîtrisés**")
        st.markdown(_pills(maitrise, "skills-match") if maitrise else "<em>aucun</em>", unsafe_allow_html=True)
    with col_b:
        st.markdown("❌ **À développer**")
        st.markdown(_pills(manquants, "skills-missing") if manquants else "<em>Profil complet 🎉</em>", unsafe_allow_html=True)
    with col_c:
        st.markdown("💡 **Atouts supplémentaires**")
        shown = bonus[:5]
        rest  = len(bonus) - 5
        txt   = _pills(shown, "skills-bonus") if shown else "<em>aucun</em>"
        if rest > 0:
            txt += f'<br><span style="color:#999;font-size:0.8em;">+ {rest} autres</span>'
        st.markdown(txt, unsafe_allow_html=True)

    # Recommandations dans un expander discret
    if recs and len(recs) > 1:
        with st.expander("📋 Voir les recommandations personnalisées"):
            for rec in recs[1:]:  # skip l'intro générique
                st.markdown(f'<div class="rec-box">💬 {rec}</div>', unsafe_allow_html=True)


def _display_compat_detail(detail: dict, score: float) -> None:
    """Affiche le détail technique des scores dans un expander."""
    # Score global
    st.markdown(_compat_global_html(score), unsafe_allow_html=True)

    # Scores individuels
    LABELS = {
        "sbert":      ("Pertinence sémantique", "🤖"),
        "competences":("Compétences",            "🛠️"),
        "experience": ("Expérience",             "📅"),
        "localisation":("Localisation",          "📍"),
        "formation":  ("Formation",              "🎓"),
    }
    cols = st.columns(5)
    for i, (key, (label, emoji)) in enumerate(LABELS.items()):
        val = detail.get(key, {})
        score_val = val if isinstance(val, float) else (val.get("score", 0) if isinstance(val, dict) else 0)
        with cols[i]:
            st.markdown(_score_card(label, score_val, emoji), unsafe_allow_html=True)

    # Expérience
    exp = detail.get("experience", {})
    if isinstance(exp, dict) and exp.get("offre") is not None:
        st.markdown("---")
        st.markdown("**📅 Expérience**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Votre expérience", f"{exp.get('cv', 0)} an(s)")
        col2.metric("Requise",          f"{exp.get('offre', 0)} an(s)")
        col3.metric("Écart",            f"{exp.get('manquantes', 0)} an(s)")

    # Localisation
    loc = detail.get("localisation", {})
    if isinstance(loc, dict):
        st.markdown("---")
        st.markdown("**📍 Localisation**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Votre ville", loc.get("cv", "N/A"))
        col2.metric("Lieu du poste", loc.get("offre", "N/A"))
        dist = loc.get("distance_km")
        col3.metric("Distance", f"{dist} km" if dist is not None else "N/A")

    # Formation
    form = detail.get("formation", {})
    if isinstance(form, dict):
        st.markdown("---")
        st.markdown("**🎓 Formation**")
        col1, col2 = st.columns(2)
        col1.metric("Votre niveau", form.get("cv", "N/A"))
        col2.metric("Niveau requis", form.get("offre", "N/A") or "Non précisé")


def _display_results(results, show_detail=True, has_cv=False):
    if not results:
        st.warning("❌ Aucune offre trouvée pour ces critères.")
        st.info("💡 Élargissez la ville au département (ex: 78 pour les Yvelines) ou supprimez le filtre ville.")
        return

    st.success(f"✅ {len(results)} offre(s) trouvée(s)")

    for offre in results:
        gap   = offre.get("skills_gap")
        taux  = gap.get("taux_match", 0) if gap else None
        score = offre.get("score", 0)

        # ── En-tête expander ─────────────────────────────────────────────
        titre     = offre.get("title", "N/A")
        lieu      = offre.get("workplace_label", "N/A")
        ref       = offre.get("id", "N/A")
        match_txt = f" · 🎯 {taux:.0f}% skills" if (has_cv and taux is not None) else ""
        header    = f"{titre} · {lieu} · Score {score:.3f}{match_txt} · Réf {ref}"

        with st.expander(header):

            # ── 1. Informations clés ──────────────────────────────────────
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📄 Contrat",    offre.get("contract_type_label") or "N/A")
            col2.metric("🧑 Expérience", offre.get("experience_label") or "N/A")
            col3.metric("💰 Salaire",    offre.get("salary_label") or "Non précisé")
            col4.metric("📅 Publié le",  (offre.get("creation_date") or "N/A")[:10])

            # ── 2. Compatibilité CV — toujours affiché si CV uploadé ─────
            if has_cv and gap:
                st.markdown("---")
                st.markdown("### 🎯 Votre compatibilité avec ce poste")
                _display_skills_gap(gap)

            # ── 3. Description (résumé + dépliable) ───────────────────────
            st.markdown("---")
            st.markdown("### 📄 Description du poste")
            description = offre.get("description", "")
            if description:
                # Affiche les 400 premiers caractères
                if len(description) > 400:
                    st.markdown(description[:400] + "…")
                    with st.expander("Lire la description complète"):
                        st.write(description)
                else:
                    st.write(description)
            else:
                st.caption("Aucune description disponible.")

            # ── 4. Détail technique (dépliable) ───────────────────────────
            if offre.get("detail") and show_detail:
                st.markdown("---")
                with st.expander("🔍 Détail de l'analyse de compatibilité (scores algorithmiques)"):
                    _display_compat_detail(offre["detail"], score)

            # ── 5. Infos entreprise ───────────────────────────────────────
            st.markdown("---")
            st.markdown("### 🏢 Informations sur l'entreprise")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Entreprise :** {offre.get('company_name') or 'N/A'}")
                st.write(f"**Secteur :** {offre.get('sector_activity_label') or 'N/A'}")
                st.write(f"**Lieu :** {offre.get('workplace_label') or 'N/A'}")
            with col2:
                st.write(f"**Source :** {offre.get('source') or 'N/A'}")
                st.write(f"**Postes ouverts :** {offre.get('number_of_positions') or 'N/A'}")
                st.write(f"**Référence :** {offre.get('id') or 'N/A'}")

            # ── 6. Bouton postuler ────────────────────────────────────────
            st.markdown("---")
            lien = (
                offre.get("application_url") or
                offre.get("recruiter_url") or
                offre.get("contact_coordinates1") or
                offre.get("contact_coordinates2") or
                offre.get("contact_coordinates3")
            )
            email    = offre.get("contact_email")
            offre_id = offre.get("id")

            if lien:
                st.link_button("🚀 Postuler maintenant", lien)
            elif email:
                st.info(f"📧 Candidature par email : **{email}**")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Référence de l'offre : **{offre_id}**")
                with col2:
                    st.link_button(
                        "🔗 Voir sur France Travail",
                        f"https://candidat.francetravail.fr/offres/recherche/detail/{offre_id}"
                    )


# ── Constantes ────────────────────────────────────────
EXPERIENCE_MAP     = {"D - Débutant": "D", "S - Souhaitée": "S", "E - Exigée": "E"}
APPRENTICESHIP_MAP = {"Oui": True, "Non": False}
all_rome_labels    = get_rome_labels()

# ── Onglets ───────────────────────────────────────────
tab1, tab2 = st.tabs(["📝 Texte libre", "📄 Upload CV (PDF)"])

# ── Tab 1 : Texte libre ───────────────────────────────
with tab1:

    st.markdown("**🏷️ Filtrer par métier**")
    rome_search    = st.text_input("Rechercher un métier",
                                   placeholder="Ex: data, infirmier, commercial...",
                                   key="tab1_rome_search")
    rome_options   = [r for r in all_rome_labels if rome_search.lower() in r.lower()] if rome_search else []
    selected_romes = st.multiselect("Sélectionner le(s) métier(s)",
                                    options=rome_options,
                                    key="tab1_rome_select")
    if rome_search and not selected_romes:
        st.caption("💡 Sélectionnez un métier dans la liste ci-dessus pour filtrer.")

    with st.form("search_form"):
        query = st.text_area(
            "Décrivez votre profil ou collez votre CV",
            placeholder="Ex: Data Engineer avec 3 ans d'expérience en Python, Spark, Airflow...",
            height=150
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            contract_type = st.selectbox("Type de contrat", ["", "CDI", "CDD", "MIS"])
        with col2:
            workplace_city = st.text_input("Ville", placeholder="Ex: Poissy")
        with col3:
            department = st.text_input("Ou département", placeholder="Ex: 78")
        with col4:
            top_n = st.slider("Nombre de résultats", 1, 50, 10)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            required_experience = st.selectbox("Expérience", ["", "D - Débutant", "S - Souhaitée", "E - Exigée"])
        with col2:
            sector = st.text_input("Secteur", placeholder="Ex: Informatique")
        with col3:
            apprenticeship = st.selectbox("Alternance", ["", "Non", "Oui"])
        with col4:
            model = st.selectbox("Modèle ML", ["tfidf", "sbert", "hybrid", "knn"],
                        help="TF-IDF = baseline, SBERT = sémantique, Hybrid = multicritères, KNN = vectoriel ES")

        show_detail = st.checkbox(
            "📊 Afficher le détail des scores (hybrid/knn)",
            value=True,
            key="tab1_show_detail",
            help="Disponible uniquement pour les modèles hybrid et knn"
        )
        submitted = st.form_submit_button("🔍 Rechercher")

    if submitted and query:
        location_filter = workplace_city or department or None
        rome_label      = selected_romes[0] if len(selected_romes) == 1 else None

        payload = {
            "query":                 query,
            "top_n":                 top_n,
            "contract_type":         contract_type or None,
            "workplace_city":        location_filter,
            "required_experience":   EXPERIENCE_MAP.get(required_experience) or None,
            "rome_label":            rome_label,
            "apprenticeship":        APPRENTICESHIP_MAP.get(apprenticeship, None),
            "sector_activity_label": sector or None,
            "show_detail":           show_detail,
        }
        with st.spinner("Recherche en cours..."):
            start   = time.time()
            r       = requests.post(f"{API_URL}/recommend/", json=payload, params={"model": model})
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model}) : **{elapsed:.2f} secondes**")
        # Pas de CV structuré sur cet onglet → has_cv=False
        _display_results(results, show_detail=show_detail, has_cv=False)


# ── Tab 2 : Upload CV ─────────────────────────────────
with tab2:
    uploaded_file = st.file_uploader("Déposez votre CV en PDF", type=["pdf"])

    st.markdown("**🏷️ Filtrer par métier**")
    rome_search_cv    = st.text_input("Rechercher un métier",
                                      placeholder="Ex: data, infirmier, commercial...",
                                      key="tab2_rome_search")
    rome_options_cv   = [r for r in all_rome_labels if rome_search_cv.lower() in r.lower()] if rome_search_cv else []
    selected_romes_cv = st.multiselect("Sélectionner le(s) métier(s)",
                                       options=rome_options_cv,
                                       key="tab2_rome_select")
    if rome_search_cv and not selected_romes_cv:
        st.caption("💡 Sélectionnez un métier dans la liste ci-dessus pour filtrer.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        contract_type_cv = st.selectbox("Type de contrat", ["", "CDI", "CDD", "MIS"], key="cv_contract")
    with col2:
        workplace_city_cv = st.text_input("Ville", placeholder="Ex: Paris", key="cv_city")
    with col3:
        department_cv = st.text_input("Ou département", placeholder="Ex: 75", key="cv_dept")
    with col4:
        top_n_cv = st.slider("Nombre de résultats", 1, 50, 10, key="cv_topn")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        required_experience_cv = st.selectbox("Expérience", ["", "D - Débutant", "S - Souhaitée", "E - Exigée"], key="cv_exp")
    with col2:
        sector_cv = st.text_input("Secteur", placeholder="Ex: Informatique", key="cv_sector")
    with col3:
        apprenticeship_cv = st.selectbox("Alternance", ["", "Non", "Oui"], key="cv_apprenticeship")
    with col4:
        model_cv = st.selectbox("Modèle ML", ["tfidf", "sbert", "hybrid", "knn"], key="cv_model",
                            help="TF-IDF = baseline, SBERT = sémantique, Hybrid = multicritères, KNN = vectoriel ES")

    show_detail_cv = st.checkbox(
        "📊 Afficher le détail des scores (hybrid/knn)",
        value=True,
        key="tab2_show_detail",
        help="Disponible uniquement pour les modèles hybrid et knn"
    )

    if uploaded_file and st.button("🔍 Rechercher par CV"):
        location_filter_cv = workplace_city_cv or department_cv or None
        rome_label_cv      = selected_romes_cv[0] if len(selected_romes_cv) == 1 else None

        params = {
            "top_n":       top_n_cv,
            "model":       model_cv,
            "show_detail": show_detail_cv,
        }
        if contract_type_cv:
            params["contract_type"] = contract_type_cv
        if location_filter_cv:
            params["workplace_city"] = location_filter_cv
        if rome_label_cv:
            params["rome_label"] = rome_label_cv
        if required_experience_cv:
            params["required_experience"] = EXPERIENCE_MAP.get(required_experience_cv)
        if sector_cv:
            params["sector_activity_label"] = sector_cv
        if apprenticeship_cv:
            params["apprenticeship"] = APPRENTICESHIP_MAP.get(apprenticeship_cv)

        with st.spinner("Analyse du CV en cours..."):
            start   = time.time()
            r       = requests.post(
                f"{API_URL}/recommend/cv",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                params=params,
            )
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model_cv}) : **{elapsed:.2f} secondes**")
        # CV uploadé → has_cv=True → affiche skills_gap
        _display_results(results, show_detail=show_detail_cv, has_cv=True)
