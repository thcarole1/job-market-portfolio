'''
settings.py centralise toutes les variables d'environnement
du projet en un seul endroit.

Au lieu de faire os.getenv("POSTGRES_HOST") partout dans le code,
tu importes l'objet settings et tu accèdes à settings.POSTGRES_HOST.

Avantages :
- Un seul endroit pour gérer la config — si tu renommes une variable,
  tu ne changes qu'ici
- Typage — Pydantic valide que POSTGRES_PORT est bien un int, pas une string
- Erreur explicite au démarrage — si une variable obligatoire est absente
  du .env, l'app refuse de démarrer avec un message clair
'''

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # remonte de config/ vers la racine

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env")


    #🗄️ PostgreSQL — credentials, nom de la base, port
    POSTGRES_HOST : str
    POSTGRES_PORT : int = 5432
    POSTGRES_DB : str
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str

    #🍃 MongoDB — idem
    MONGO_HOST : str
    MONGO_PORT : int =27017
    MONGO_INITDB_ROOT_USERNAME : str
    MONGO_INITDB_ROOT_PASSWORD : str

    #🔍 Elasticsearch — hôte, port
    ELASTIC_HOST : str
    ELASTIC_PORT : int = 9200
    ELASTICSEARCH_INDEX : str

    #🔑 API France Travail — clés d'authentification
    FRANCETRAVAIL_CLIENT_ID : str
    FRANCETRAVAIL_CLIENT_SECRET : str

    #PGADMIN
    PGADMIN_EMAIL : str
    PGADMIN_PASSWORD : str

    #⚙️ Applicatif — environnement (dev/prod), ports exposés
    ENVIRONMENT : str = 'dev'            # dev | prod — change le comportement des logs, erreurs, etc.
    LOG_LEVEL : str   = 'INFO'              # DEBUG | INFO | WARNING | ERROR

    # Ports exposés sur ta machine hôte (le côté gauche du ":" dans docker-compose)
    #Pourquoi les ports dans .env ? Pour éviter les conflits entre développeurs —
    #si quelqu'un a déjà quelque chose sur le port 8000, il change juste son .env
    #sans toucher au docker-compose.yml.
    API_PORT :int
    INGESTION_PORT : int
    FRONTEND_PORT : int


settings = Settings()
