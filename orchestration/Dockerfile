FROM apache/airflow:2.9.1

# Installer les dépendances du projet job-market-portfolio
RUN pip install --no-cache-dir \
    pydantic==2.13.3 \
    pydantic-settings==2.14.0 \
    pymongo==4.17.0 \
    elasticsearch==8.17.0 \
    sentence-transformers==5.4.1 \
    python-dotenv==1.2.2 \
    requests==2.33.1
