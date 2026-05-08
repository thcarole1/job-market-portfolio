import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Recherche", page_icon="🔍", layout="wide")
st.title("🔍 Recherche d'offres par profil")


def _display_results(results):
    if len(results) == 0:
        st.warning("❌ Aucune offre trouvée pour ces critères.")
        st.info("💡 Suggestions : élargissez la ville au département (ex: 78 pour les Yvelines), ou supprimez le filtre ville.")
        return

    st.success(f"{len(results)} offres trouvées")
    st.markdown("---")

    for offre in results:
        with st.expander(f"**{offre.get('title', 'N/A')}** — {offre.get('workplace_label', 'N/A')} — Score: {offre.get('score', 0):.3f}"):

            col1, col2, col3 = st.columns(3)
            col1.metric("Contrat", offre.get('contract_type_label') or 'N/A')
            col2.metric("Expérience", offre.get('experience_label') or 'N/A')
            col3.metric("Postes", offre.get('number_of_positions') or 'N/A')

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Informations")
                st.write(f"**Entreprise:** {offre.get('company_name') or 'N/A'}")
                st.write(f"**Lieu:** {offre.get('workplace_label') or 'N/A'}")
                st.write(f"**Salaire:** {offre.get('salary_label') or 'N/A'}")
                st.write(f"**Secteur:** {offre.get('sector_activity_label') or 'N/A'}")
                st.write(f"**Source:** {offre.get('source') or 'N/A'}")
                st.write(f"**Publié le:** {(offre.get('creation_date') or 'N/A')[:10]}")
            with col2:
                st.subheader("Compétences requises")
                for c in offre.get('competences', []):
                    st.write(f"- {c.get('libelle')}")
                st.subheader("Langues")
                for l in offre.get('languages', []):
                    st.write(f"- {l.get('libelle')} ({l.get('exigence')})")

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
        model = st.selectbox("Modèle ML", ["tfidf", "sbert"],
                    help="TF-IDF = baseline rapide, SBERT = sémantique")
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
            r = requests.post(f"{API_URL}/recommend/", json=payload, params={"model": model})
            results = r.json()
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

    model_cv = st.selectbox("Modèle ML", ["tfidf", "sbert"], key="cv_model",
                        help="TF-IDF = baseline rapide, SBERT = sémantique")

    if uploaded_file and st.button("🔍 Rechercher par CV"):
        location_filter_cv = workplace_city_cv or department_cv or None
        params = {"top_n": top_n_cv}
        if contract_type_cv:
            params["contract_type"] = contract_type_cv
        if location_filter_cv:
            params["workplace_city"] = location_filter_cv

        params["model"] = model_cv

        with st.spinner("Analyse du CV en cours..."):
            r = requests.post(
                f"{API_URL}/recommend/cv",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                params=params
            )
            results = r.json()
        _display_results(results)
