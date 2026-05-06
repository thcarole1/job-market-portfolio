# api/Dockerfile

# Image de base — Python 3.12 léger
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier les dépendances en premier
# (optimisation Docker — cette couche est mise en cache si requirements.txt ne change pas)
COPY  requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code du projet
COPY . .

# Créer et basculer vers un utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Port sur lequel l'API écoute
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "services.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
