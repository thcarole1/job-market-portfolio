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
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_rome_labels():
    try:
        r = requests.get(f"{API_URL}/offers/rome-labels")
        return sorted(r.json())
    except:
        return []


def _display_results(results, show_detail=True):
    if len(results) == 0:
        st.warning("❌ Aucune offre trouvée pour ces critères.")
        st.info("💡 Suggestions : élargissez la ville au département (ex: 78 pour les Yvelines), ou supprimez le filtre ville.")
        return

    st.success(f"{len(results)} offres trouvées")
    st.markdown("---")

    for offre in results:
        with st.expander(f"**{offre.get('title', 'N/A')}** — {offre.get('workplace_label', 'N/A')} — Score: {offre.get('score', 0):.3f} — Réf: {offre.get('id', 'N/A')}"):

            col1, col2, col3 = st.columns(3)
            col1.metric("Contrat", offre.get('contract_type_label') or 'N/A')
            col2.metric("Expérience", offre.get('experience_label') or 'N/A')
            col3.metric("Postes", offre.get('number_of_positions') or 'N/A')

            if offre.get("detail") and show_detail:
                detail = offre["detail"]
                st.markdown("### 📊 Analyse de compatibilité")

                st.metric("🏆 Score hybride global", f"{offre.get('score', 0):.3f} / 1.000")
                st.markdown("---")

                st.markdown("**🤖 Similarité sémantique (SBERT)**")
                st.metric("Score SBERT", f"{detail.get('sbert', 0):.2f}")
                st.markdown("---")

                comp = detail.get("competences", {})
                if isinstance(comp, dict):
                    st.markdown("**🛠️ Compétences**")
                    st.metric("Score compétences", f"{comp.get('score', 0):.2f}")
                    if comp.get("offre"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("✅ **Maîtrisées**")
                            for c in comp.get("match", []):
                                st.markdown(f"- {c}")
                        with col2:
                            st.markdown("❌ **Manquantes**")
                            manquantes = comp.get("manquantes", [])
                            if manquantes:
                                for c in manquantes:
                                    st.markdown(f"- {c}")
                            else:
                                st.markdown("*Aucune — profil complet* 🎉")
                st.markdown("---")

                exp = detail.get("experience", {})
                if isinstance(exp, dict):
                    st.markdown("**📅 Expérience**")
                    st.metric("Score expérience", f"{exp.get('score', 0):.2f}")
                    if exp.get("offre") is not None:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("CV",        f"{exp.get('cv', 0)} an(s)")
                        col2.metric("Requise",   f"{exp.get('offre', 0)} an(s)")
                        col3.metric("Manquante", f"{exp.get('manquantes', 0)} an(s)")
                    else:
                        st.info("Expérience non précisée dans l'offre")
                st.markdown("---")

                loc = detail.get("localisation", {})
                if isinstance(loc, dict):
                    st.markdown("**📍 Localisation**")
                    st.metric("Score localisation", f"{loc.get('score', 0):.2f}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("CV",    loc.get("cv", "N/A"))
                    col2.metric("Offre", loc.get("offre", "N/A"))
                    distance = loc.get("distance_km")
                    col3.metric("Distance", f"{distance} km" if distance is not None else "N/A")
                st.markdown("---")

                form = detail.get("formation", {})
                if isinstance(form, dict):
                    st.markdown("**🎓 Formation**")
                    st.metric("Score formation", f"{form.get('score', 0):.2f}")
                    col1, col2 = st.columns(2)
                    col1.metric("CV",      form.get("cv", "N/A"))
                    col2.metric("Requise", form.get("offre", "N/A"))
                st.markdown("---")

            st.markdown("---")
            st.subheader("Informations")
            st.write(f"**Entreprise:** {offre.get('company_name') or 'N/A'}")
            st.write(f"**Lieu:** {offre.get('workplace_label') or 'N/A'}")
            st.write(f"**Salaire:** {offre.get('salary_label') or 'N/A'}")
            st.write(f"**Secteur:** {offre.get('sector_activity_label') or 'N/A'}")
            st.write(f"**Source:** {offre.get('source') or 'N/A'}")
            st.write(f"**Publié le:** {(offre.get('creation_date') or 'N/A')[:10]}")

            st.markdown("---")
            st.subheader("Description complète")
            st.write(offre.get('description', 'N/A'))

            st.markdown("---")
            st.subheader("Postuler")
            lien_candidature = (
                offre.get('application_url') or
                offre.get('recruiter_url') or
                offre.get('contact_coordinates1') or
                offre.get('contact_coordinates2') or
                offre.get('contact_coordinates3')
            )
            email    = offre.get('contact_email')
            offre_id = offre.get('id')

            if lien_candidature:
                st.markdown(f"[🔗 Postuler ici]({lien_candidature})", unsafe_allow_html=True)
            elif email:
                st.write(f"📧 Candidature par email : {email}")
            else:
                st.info(f"Aucun lien disponible — Référence de l'offre : **{offre_id}**")
                st.markdown(f"[🔗 Rechercher sur France Travail](https://candidat.francetravail.fr/offres/recherche/detail/{offre_id})")


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
            "📊 Afficher l'analyse de compatibilité",
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
            "show_detail":           show_detail
        }
        with st.spinner("Recherche en cours..."):
            start   = time.time()
            r       = requests.post(f"{API_URL}/recommend/", json=payload, params={"model": model})
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model}) : **{elapsed:.2f} secondes**")
        _display_results(results, show_detail=show_detail)


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
        "📊 Afficher l'analyse de compatibilité",
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
            "show_detail": show_detail_cv
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
                params=params
            )
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model_cv}) : **{elapsed:.2f} secondes**")
        _display_results(results, show_detail=show_detail_cv)
