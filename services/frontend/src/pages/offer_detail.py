import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Détail offre", page_icon="📄", layout="wide")
st.title("📄 Détail de l'offre")

offer_id = st.session_state.get('selected_offer_id')

if not offer_id:
    offer_id = st.text_input("Entrez un ID d'offre", placeholder="Ex: 207TJNQ")

if offer_id:
    with st.spinner("Chargement..."):
        r = requests.get(f"{API_URL}/offers/{offer_id}")
        if r.status_code == 404:
            st.error("Offre non trouvée")
        else:
            offre = r.json()

            st.header(offre.get('title', 'N/A'))
            st.markdown("---")

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
            st.subheader("Description")
            st.write(offre.get('description', 'N/A'))

            if offre.get('contact_coordinates1'):
                st.markdown("---")
                st.subheader("Postuler")
                st.write(offre.get('contact_coordinates1'))
