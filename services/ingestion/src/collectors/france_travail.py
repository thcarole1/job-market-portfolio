
import requests
import logging
logger = logging.getLogger(__name__)

from config.settings import settings

class FranceTravailCollector:

    def __init__(self):
        self._token = None

    def _get_token(self):
        """Récupère un token d'authentification OAuth2."""

        logger.info("Début de l'opération de récupération du token France Travail")

        try:
            url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
            params = {"realm": "/partenaire"}
            data = {
                "grant_type":    "client_credentials",
                "client_id":     settings.FRANCETRAVAIL_CLIENT_ID,
                "client_secret": settings.FRANCETRAVAIL_CLIENT_SECRET,
                "scope":         "api_offresdemploiv2 o2dsoffre"
            }
            response = requests.post(url, params=params, data=data)
            response.raise_for_status()
            logger.info("Opération de récupération de token réussie")
            self._token= response.json()["access_token"]
            return self._token
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP : {e}")
            raise

    def _search_offers(self,
                       mots_cles = None,
                       rome_code=None,
                       range_str = "0-149"):
        """Recherche des offres d'emploi via l'API FranceTravail.
        Retourne un dictionnaire global avec une liste d'offres et d'autres informations (filtres possibles)"""

        logger.info(f"Début de l'opération de récupération d'offres France Travail - Range {range_str}")
        if self._token is None:
            self._get_token()

        try:
            url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
            headers = {
                "Authorization": f"Bearer {self._token}",
                "Accept":        "application/json"
            }
            params = {
                "motsCles":   mots_cles,
                "range":      range_str,
                "sort":       "1"
            }

            if rome_code:
                params["codeROME"] = rome_code

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            if not response.text:
                logger.warning(f"Réponse vide pour le range {range_str}")
                return {"resultats": []}

            logger.info("Opération de récupération des offres réussie")
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP : {e}")
            raise

    def collect_all_offers(self,mots_cles=None, rome_codes=None):
        """
        Recherche de toutes les offres d'emploi via l'API FranceTravail.
        - mots_cles : filtre par mots clés
        - rome_codes : liste de codes ROME à collecter
        Si rome_codes est fourni, boucle sur chaque code ROME.
        """

        logger.info("Début de l'opération de récupération de toutes les offres France Travail")

        try :
            start, stop, step = 0, 3149, 150
            ranges = [f"{start}-{min(start+step-1, stop)}" for start in range (start, stop, step)]
            offres = []
            ids_collectes = set()  # ← évite les doublons entre codes ROME

            codes = rome_codes if rome_codes else [None]

            for code in codes:
                logger.info(f"Collecte pour le code ROME : {code or 'tous'}")
                for range_unit in ranges:
                    resultats = self._search_offers(
                        mots_cles=mots_cles,
                        rome_code=code,
                        range_str=range_unit
                    )
                    if not resultats["resultats"]:
                        logger.info(f"Plus d'offres à partir du range {range_unit}, arrêt de la collecte")
                        break
                    # Déduplique par id
                    for offre in resultats["resultats"]:
                        if offre["id"] not in ids_collectes:
                            offres.append(offre)
                            ids_collectes.add(offre["id"])

            logger.info(f"Opération de récupération de toutes les offres réussie — {len(offres)} offres collectées")
            return offres

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP : {e}")
            raise
