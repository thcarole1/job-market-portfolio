import requests
import logging

logger = logging.getLogger(__name__)

from config.settings import settings


class FranceTravailCollector:

    def __init__(self):
        self._token = None

    def _get_token(self):
        """Récupère un token d'authentification OAuth2."""
        logger.info("Récupération du token France Travail...")
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
            self._token = response.json()["access_token"]
            logger.info("Token récupéré ✅")
            return self._token
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP token : {e}")
            raise

    def _search_offers(
        self,
        mots_cles=None,
        rome_code=None,
        range_str="0-149",
        min_creation_date=None,
    ):
        """
        Recherche des offres via l'API France Travail.

        Paramètres
        ----------
        min_creation_date : str | None
            Format ISO 8601 : "2024-01-15T00:00:00Z"
            Si fourni, ne retourne que les offres publiées après cette date.
        """
        logger.info(
            f"Recherche offres — ROME={rome_code or 'tous'} range={range_str}"
            + (f" depuis={min_creation_date}" if min_creation_date else "")
        )

        if self._token is None:
            self._get_token()

        try:
            url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
            headers = {
                "Authorization": f"Bearer {self._token}",
                "Accept":        "application/json"
            }
            params = {
                "motsCles": mots_cles,
                "range":    range_str,
                "sort":     "1"
            }
            if rome_code:
                params["codeROME"] = rome_code

            query_string = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


            if min_creation_date:
                from datetime import datetime, timezone
                max_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                query_string += f"&minCreationDate={min_creation_date}&maxCreationDate={max_date}"

            response = requests.get(f"{url}?{query_string}", headers=headers)
            response.raise_for_status()

            if not response.text:
                logger.warning(f"Réponse vide pour le range {range_str}")
                return {"resultats": []}

            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP search : {e}")
            raise

    def collect_all_offers(
        self,
        mots_cles=None,
        rome_codes=None,
        existing_ids=None,
        min_creation_date=None,
    ):
        """
        Collecte les offres France Travail.

        Paramètres
        ----------
        existing_ids : set | None
            IDs déjà présents en base — préparés par main.py.
            Filtre appliqué après chaque page de résultats.
        min_creation_date : str | None
            Date ISO 8601 passée à l'API pour filtrer les offres anciennes.
            Préparée par main.py depuis la date de la dernière offre en base.
            Exemple : "2024-01-15T00:00:00Z"
        """
        existing_ids = existing_ids or set()
        mode = "incrémental" if existing_ids or min_creation_date else "complet"
        logger.info(f"Début collecte France Travail — mode {mode}")

        try:
            start, stop, step = 0, 3149, 150
            ranges = [
                f"{start}-{min(start + step - 1, stop)}"
                for start in range(start, stop, step)
            ]
            offres = []
            ids_collectes = set()  # doublons entre codes ROME dans la même session

            codes = rome_codes if rome_codes else [None]

            for code in codes:
                logger.info(f"Collecte ROME : {code or 'tous'}")
                for range_unit in ranges:
                    resultats = self._search_offers(
                        mots_cles=mots_cles,
                        rome_code=code,
                        range_str=range_unit,
                        min_creation_date=min_creation_date,
                    )

                    if not resultats["resultats"]:
                        logger.info(f"Plus d'offres à partir du range {range_unit}, arrêt")
                        break

                    n_avant = len(offres)
                    for offre in resultats["resultats"]:
                        offre_id = offre["id"]
                        if offre_id in ids_collectes:   # doublon session
                            continue
                        if offre_id in existing_ids:    # déjà en base
                            continue
                        offres.append(offre)
                        ids_collectes.add(offre_id)

                    n_nouvelles = len(offres) - n_avant
                    logger.info(f"  Range {range_unit} : {n_nouvelles} nouvelles offres")

            logger.info(f"Collecte terminée — {len(offres)} nouvelles offres")
            return offres

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP collecte : {e}")
            raise
