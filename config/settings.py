from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")


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


    #⚙️ Applicatif — environnement (dev/prod), ports exposés
    ENVIRONMENT : str = 'dev'            # dev | prod — change le comportement des logs, erreurs, etc.
    LOG_LEVEL : str   = 'INFO'              # DEBUG | INFO | WARNING | ERROR

    # Ports exposés sur ta machine hôte (le côté gauche du ":" dans docker-compose)
    #Pourquoi les ports dans .env ? Pour éviter les conflits entre développeurs —
    #si quelqu'un a déjà quelque chose sur le port 8000, il change juste son .env
    #sans toucher au docker-compose.yml.
    API_PORT :int
    INGESTION_PORT : int


settings = Settings()
