from pymongo import MongoClient, errors
import logging
logger = logging.getLogger(__name__)

from config.settings import settings

class Mongoloader:
    def __init__(self):
        '''connexion à MongoDB '''
        logger.info("Instanciation de Mongoloader - Tentative de connexion à Mongodb")
        try:
            self.client = MongoClient(f"mongodb://{settings.MONGO_INITDB_ROOT_USERNAME}:{settings.MONGO_INITDB_ROOT_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/")
            self.db = self.client["job_market"]
            logger.info("Instanciation de Mongoloader - Connexion à Mongodb réussie !")
        except errors.PyMongoError as e:
            logger.error(f"Erreur connexion à Mongodb : {e}")
            raise


    def insert_raw_offer(self, offer: dict, collection = None):
        '''insère dans offres_brutes avec upsert'''
        logger.info("Insertion d'une offre brute dans Mongodb")
        try:
            collection = self.db["offres_brutes"]
            collection.update_one(
                                    {"id": offer["id"]},   # filtre — cherche par id
                                    {"$set": offer},       # mise à jour
                                    upsert=True            # insère si absent
                                )
            logger.info("Insertion d'une offre brute dans Mongodb réussie !")
        except errors.PyMongoError as e:
            logger.error(f"Erreur insertion offre brute dans Mongodb : {e}")
            raise


    def insert_normalized_offer(self, offer: dict, collection = None):
        '''insère dans offres_normalisees avec upsert'''
        logger.info("Insertion d'une offre normalisée dans Mongodb")
        try:
            collection = self.db["offres_normalisees"]
            collection.update_one(
                                    {"id": offer["id"]},   # filtre — cherche par id
                                    {"$set": offer},       # mise à jour
                                    upsert=True            # insère si absent
                                )
            logger.info("Insertion d'une offre normalisée dans Mongodb réussie !")
        except errors.PyMongoError as e:
            logger.error(f"Erreur insertion offre normalisée dans Mongodb : {e}")
            raise
