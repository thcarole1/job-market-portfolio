import pdfplumber
import io
import unicodedata
import logging
logger = logging.getLogger(__name__)

class CVParser:
    def __init__(self):
        pass

    def parse(self, file_bytes: bytes, file_type: str) -> str :
        """
        Point d'entrée public du CVParser.
        Extrait et nettoie le texte d'un CV selon son type de fichier.
        Supporte actuellement : pdf
        Lève une ValueError si le type de fichier n'est pas supporté.
        """
        logger.info("Début de l'extraction du texte du CV.")
        if file_type == "pdf":
            extractedt_text = self._extract_from_pdf(file_bytes)
            clean_text = self._clean_text(extractedt_text)
            logger.info("Fin de l'extraction du texte du CV.")
            return clean_text
        else :
            raise ValueError(f"Type de fichier non supporté : {file_type}")

    def _extract_from_pdf(self, file_bytes: bytes) -> str :
        """
        Extrait le texte brut d'un fichier PDF page par page.
        Retourne le texte de toutes les pages concaténées.
        Les pages vides sont ignorées.
        """
        logger.info("Début de l'extraction du CV au format PDF.")
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages)

        logger.info("Fin de l'extraction du CV au format PDF.")
        return text

    def _clean_text(self, text: str) -> str :
        """
        Nettoie et normalise le texte extrait d'un CV en préservant la structure.
        - Normalise les caractères Unicode (NFKC)
        - Remplace les tirets typographiques par des tirets simples
        - Supprime les caractères non imprimables
        - Supprime les espaces multiples à l'intérieur de chaque ligne
        - Supprime les lignes vides
        - Préserve les sauts de ligne pour le parsing structuré futur
        """
        logger.info("Début du nettoyage du texte du CV extrait.")
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\u2014", "-").replace("\u2013", "-")
        text = "".join(c for c in text if c.isprintable() or c == "\n")
        lines = text.split("\n")
        lines = [" ".join(line.split()) for line in lines if line.strip()]
        text = "\n".join(lines)
        logger.info("Fin du nettoyage du texte du CV extrait.")
        return text
