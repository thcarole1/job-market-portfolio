import pytest
from services.ml.src.cv_structurer import CVStructurer

structurer = CVStructurer()

def test_extract_competences_detecte_python():
    text = "Je maîtrise Python et SQL pour l'analyse de données."
    result = structurer._extract_competences(text)
    assert "Python" in result
    assert "SQL" in result

def test_extract_competences_pas_de_faux_positif_R():
    text = "Je sais travailler en équipe et rechercher des solutions."
    result = structurer._extract_competences(text)
    assert "R" not in result

def test_extract_competences_detecte_power_bi():
    text = "Expérience avec Power BI et PowerBI pour les dashboards."
    result = structurer._extract_competences(text)
    assert "Power BI" in result

def test_extract_competences_pas_de_doublons():
    text = "Python Python Python SQL SQL"
    result = structurer._extract_competences(text)
    assert result.count("Python") == 1
    assert result.count("SQL") == 1

def test_extract_experience_annees_explicites():
    text = "J'ai 5 ans d'expérience en data engineering."
    result = structurer._extract_experience(text)
    assert result == 5

def test_extract_experience_zero_si_aucune():
    text = "Profil junior sans expérience mentionnée."
    result = structurer._extract_experience(text)
    assert result == 0

def test_extract_localisation_ville_connue():
    text = "Je réside à Paris et cherche un poste en CDI."
    result = structurer._extract_localisation(text)
    assert result == "Paris"

def test_extract_localisation_non_precise():
    text = "Disponible immédiatement pour tout poste."
    result = structurer._extract_localisation(text)
    assert result == "Non précisé"

def test_extract_formation_master():
    text = "Diplômé d'un Master en informatique à Paris."
    result = structurer._extract_formation(text)
    assert result == "Master"

def test_extract_formation_non_precise():
    text = "Profil autodidacte sans diplôme mentionné."
    result = structurer._extract_formation(text)
    assert result == "Non précisé"

def test_extract_langues_anglais():
    text = "Je parle Français et Anglais couramment."
    result = structurer._extract_langues(text)
    assert "Anglais" in result
    assert "Français" in result
