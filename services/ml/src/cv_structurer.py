import re
import logging

logger = logging.getLogger(__name__)

from services.ml.src.constants import (
    COMPETENCES_CONNUES,
    NIVEAUX_FORMATION,
    LANGUES_PRATIQUEES,
    VILLES_CONNUES
)

PATTERNS_EXPERIENCE = [
    r'(\d+)\s*an[s]?',
    r'(\d+)\s*an\(s\)',
    r'(\d+)\s*ann[ée][e]?s?',
    r'(\d+)\s*year[s]?'
]

PATTERNS_PERIODES = [
    # 2022-2023 ou 2022–2023
    r'(20\d{2})\s*[-–]\s*(20\d{2})\s*[|:\-]?\s*(.{0,60})',
    # 01/2018-03/2021 ou 01/2018–03/2021
    r'\d{1,2}/(\d{4})\s*[-–]\s*\d{1,2}/(\d{4})\s*[|:\-]?\s*(.{0,60})',
    # 01/01/2018-06/03/2021
    r'\d{1,2}/\d{1,2}/(20\d{2})\s*[-–]\s*\d{1,2}/\d{1,2}/(20\d{2})\s*[|:\-]?\s*(.{0,60})',
    # Jan 2018 - Mar 2021 ou Jan/2018-Mar/2021
    r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
    r'jan|fev|mar|avr|mai|jui|jul|aou|sep|oct|nov|dec)'
    r'[a-z]*[/\s]*(20\d{2})\s*[-–]\s*'
    r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
    r'jan|fev|mar|avr|mai|jui|jul|aou|sep|oct|nov|dec)'
    r'[a-z]*[/\s]*(20\d{2})\s*[|:\-]?\s*(.{0,60})',
]

MOTS_EXPERIENCE = ["engineer", "ingénieur", "développeur", "consultant",
                   "stage", "alternance", "analyst", "manager", "lead",
                   "senior", "junior", "cdi", "cdd", "intérim"]

MOTS_FORMATION = ["master", "licence", "bachelor", "bac", "université",
                  "université", "école", "diplôme", "formation", "cursus"]

class CVStructurer:
    def extract(self, cv_text: str) -> dict:
        """
        Extrait les informations structurées du CV.
        Retourne un dict avec compétences, expérience, localisation, formation, langues.
        """
        logger.info("Extraction des informations structurées du CV...")
        return {
            "competences": self._extract_competences(cv_text),
            "annees_experience": self._extract_experience(cv_text),
            "localisation": self._extract_localisation(cv_text),
            "formation": self._extract_formation(cv_text),
            "langues": self._extract_langues(cv_text)
        }

    def _extract_competences(self, text: str) -> list:
        """Détecte les compétences techniques connues dans le texte."""
        competences_list = []
        for competence in COMPETENCES_CONNUES:
            if competence.lower() in text.lower():
                competences_list.append(competence)
        return competences_list

    def _extract_experience(self, text: str) -> int:
        """
        Extrait le nombre d'années d'expérience.
        - Méthode 1 : patterns explicites "3 ans", "5 An(s)"
        - Méthode 2 : somme des périodes professionnelles
          Supporte : 2022-2023, 01/2018-03/2021,
                     01/01/2018-06/03/2021, Jan 2018-Mar 2021
        Priorité aux mentions explicites, sinon somme des périodes.
        """
        annees_explicites = []
        annees_periodes = []

        # Méthode 1 — patterns explicites
        for pattern in PATTERNS_EXPERIENCE:
            matches = re.findall(pattern, text, re.IGNORECASE)
            annees_explicites.extend([int(m) for m in matches if int(m) <= 30])

        # Méthode 2 — périodes
        for pattern in PATTERNS_PERIODES:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                debut = int(match.group(1))
                fin = int(match.group(2))
                contexte = match.group(3).lower()
                duree = fin - debut
                if 0 < duree <= 10:
                    if any(mot in contexte for mot in MOTS_FORMATION):
                        continue
                    annees_periodes.append(duree)

        if annees_explicites:
            return max(annees_explicites)
        return sum(annees_periodes)

    def _extract_localisation(self, text: str) -> str:
        """
        Extrait la ville ou le département.
        - Méthode 1 : liste de grandes villes connues
        - Méthode 2 : pattern "Ville, France" ou "Ville, 75xxx"
        - Méthode 3 : ville sur la même ligne que email/téléphone
        - Méthode 4 : code postal → département
        """
        for ville in VILLES_CONNUES:
            if ville.lower() in text.lower():
                return ville

        match = re.search(r'([A-ZÀ-Ÿ][a-zà-ÿ\-]+),?\s*(France|\d{5})', text)
        if match:
            return match.group(1)

        match = re.search(r'\|\s*([A-ZÀ-Ÿ][a-zà-ÿ\- ]+)\s*$', text, re.MULTILINE)
        if match:
            return match.group(1).strip()

        match = re.search(r'\b(\d{5})\b', text)
        if match:
            return match.group(1)[:2]

        return "Non précisé"

    def _extract_formation(self, text: str) -> str:
        """Extrait le niveau de formation le plus élevé."""
        top_formation = "Non précisé"
        for niveau in NIVEAUX_FORMATION:
            if niveau in text:
                top_formation = niveau
        return top_formation

    def _extract_langues(self, text: str) -> list:
        """Extrait les langues mentionnées."""
        # Cherche Français, Anglais, Espagnol, Allemand...
        langues_list=[]
        for langue in LANGUES_PRATIQUEES:
            if langue.lower() in text.lower():
                langues_list.append(langue)

        if "Francais" in langues_list and "Français" not in langues_list:
            langues_list = [l.replace("Francais", "Français") for l in langues_list]
        return langues_list
