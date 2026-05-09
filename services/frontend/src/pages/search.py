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

def _display_results(results):
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

            if offre.get("detail"):
                detail = offre["detail"]
                st.markdown("### 📊 Analyse de compatibilité")

                # ── Score hybride global ──────────────────────────
                st.metric("🏆 Score hybride global", f"{offre.get('score', 0):.3f} / 1.000")
                st.markdown("---")

                # ── SBERT ─────────────────────────────────────────
                st.markdown("**🤖 Similarité sémantique (SBERT)**")
                st.metric("Score SBERT", f"{detail.get('sbert', 0):.2f}")
                st.markdown("---")

                # ── Compétences ───────────────────────────────────
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

                # ── Expérience ────────────────────────────────────
                exp = detail.get("experience", {})
                if isinstance(exp, dict):
                    st.markdown("**📅 Expérience**")
                    st.metric("Score expérience", f"{exp.get('score', 0):.2f}")
                    if exp.get("offre") is not None:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("CV",       f"{exp.get('cv', 0)} an(s)")
                        col2.metric("Requise",  f"{exp.get('offre', 0)} an(s)")
                        col3.metric("Manquante", f"{exp.get('manquantes', 0)} an(s)")
                    else:
                        st.info("Expérience non précisée dans l'offre")
                st.markdown("---")

                # ── Localisation ──────────────────────────────────
                loc = detail.get("localisation", {})
                if isinstance(loc, dict):
                    st.markdown("**📍 Localisation**")
                    st.metric("Score localisation", f"{loc.get('score', 0):.2f}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("CV",     loc.get("cv", "N/A"))
                    col2.metric("Offre",  loc.get("offre", "N/A"))
                    distance = loc.get("distance_km")
                    col3.metric("Distance", f"{distance} km" if distance is not None else "N/A")
                st.markdown("---")

                # ── Formation ─────────────────────────────────────
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
            email = offre.get('contact_email')
            offre_id = offre.get('id')

            if lien_candidature:
                st.markdown(f"[🔗 Postuler ici]({lien_candidature})", unsafe_allow_html=True)
            elif email:
                st.write(f"📧 Candidature par email : {email}")
            else:
                st.info(f"Aucun lien disponible — Référence de l'offre : **{offre_id}**")
                st.markdown(f"[🔗 Rechercher sur France Travail](https://candidat.francetravail.fr/offres/recherche/detail/{offre_id})")


# ── Onglets ───────────────────────────────────────────
tab1, tab2 = st.tabs(["📝 Texte libre", "📄 Upload CV (PDF)"])

# ── Tab 1 : Texte libre ───────────────────────────────
with tab1:
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
        model = st.selectbox("Modèle ML", ["tfidf", "sbert", "hybrid"],
                     help="TF-IDF = baseline, SBERT = sémantique, Hybrid = multicritères")
        submitted = st.form_submit_button("🔍 Rechercher")

    if submitted and query:
        location_filter = workplace_city or department or None
        payload = {
            "query": query,
            "top_n": top_n,
            "contract_type": contract_type or None,
            "workplace_city": location_filter
        }
        with st.spinner("Recherche en cours..."):
            import time
            start = time.time()
            r = requests.post(f"{API_URL}/recommend/", json=payload, params={"model": model})
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model}) : **{elapsed:.2f} secondes**")
        _display_results(results)

# ── Tab 2 : Upload CV ─────────────────────────────────
with tab2:
    uploaded_file = st.file_uploader("Déposez votre CV en PDF", type=["pdf"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        contract_type_cv = st.selectbox("Type de contrat", ["", "CDI", "CDD", "MIS"], key="cv_contract")
    with col2:
        workplace_city_cv = st.text_input("Ville", placeholder="Ex: Paris", key="cv_city")
    with col3:
        department_cv = st.text_input("Ou département", placeholder="Ex: 75", key="cv_dept")
    with col4:
        top_n_cv = st.slider("Nombre de résultats", 1, 50, 10, key="cv_topn")

    model_cv = st.selectbox("Modèle ML", ["tfidf", "sbert", "hybrid"], key="cv_model",
                        help="TF-IDF = baseline, SBERT = sémantique, Hybrid = multicritères")

    if uploaded_file and st.button("🔍 Rechercher par CV"):
        location_filter_cv = workplace_city_cv or department_cv or None
        params = {"top_n": top_n_cv}
        if contract_type_cv:
            params["contract_type"] = contract_type_cv
        if location_filter_cv:
            params["workplace_city"] = location_filter_cv
        params["model"] = model_cv

        with st.spinner("Analyse du CV en cours..."):
            import time
            start = time.time()
            r = requests.post(
                f"{API_URL}/recommend/cv",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                params=params
            )
            elapsed = time.time() - start
            results = r.json()

        st.info(f"⏱️ Temps de recherche ({model_cv}) : **{elapsed:.2f} secondes**")
        _display_results(results)
