# ml/Dockerfile

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

# Créer l'utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser

# Créer le dossier models et donner les permissions avant de changer d'utilisateur
RUN mkdir -p /app/services/ml/models && \
    chown -R appuser:appuser /app/services/ml/models

# Basculer vers l'utilisateur non-root
USER appuser

# Commande de démarrage
CMD ["python", "services/ml/src/main.py"]
