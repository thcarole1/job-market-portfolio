# ingestion/Dockerfile

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

# PYTHONPATH — permet les imports depuis la racine du projet
ENV PYTHONPATH=/app

# Créer et basculer vers un utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Commande de démarrage
CMD ["tail", "-f", "/dev/null"]
