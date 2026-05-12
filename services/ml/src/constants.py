# ── Compétences techniques connues ────────────────────
COMPETENCES_CONNUES = [
    # ── Langages de programmation ─────────────────────
    "Python", "SQL", "Scala", "Java", "Langage R", "Julia",
    "Go", "Rust", "C++", "C#", "JavaScript", "TypeScript",
    "Bash", "Shell", "Perl",

    # ── Frameworks & librairies Python ────────────────
    "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "plotly", "scikit-learn", "statsmodels", "xgboost",
    "LightGBM", "CatBoost", "TensorFlow", "Keras",
    "PyTorch", "FastAI",
    "spaCy", "NLTK", "OpenCV", "Pillow",
    "FastAPI", "Flask", "Django", "Streamlit", "Gradio",
    "SQLAlchemy", "Pydantic", "Celery",

    # ── Big Data & traitement distribué ───────────────
    "Spark", "PySpark", "Hadoop", "Hive",
    "Flink", "Storm", "Beam", "Pig", "MapReduce",
    "Presto", "Trino", "Impala", "Drill",
    "Delta Lake", "Iceberg", "Hudi",

    # ── Streaming & messaging ─────────────────────────
    "Kafka", "RabbitMQ", "Pulsar", "Kinesis",
    "Pub/Sub", "NATS", "ActiveMQ", "EventHub",

    # ── Orchestration & pipeline ──────────────────────
    "Airflow", "Prefect", "Dagster", "Luigi",
    "Argo", "Kubeflow", "MLflow", "ZenML",
    "dbt", "Fivetran", "Stitch", "Airbyte",
    "Informatica", "Talend", "DataStage", "SSIS",

    # ── Bases de données relationnelles ───────────────
    "PostgreSQL", "MySQL", "MariaDB", "Oracle",
    "SQL Server", "SQLite", "Redshift",
    "Snowflake", "Teradata", "Greenplum",

    # ── Bases de données NoSQL ────────────────────────
    "MongoDB", "Cassandra", "HBase", "DynamoDB",
    "Couchbase", "CouchDB", "Neo4j", "ArangoDB",
    "InfluxDB", "TimescaleDB", "Druid",

    # ── Cache & recherche ─────────────────────────────
    "Redis", "Memcached", "Elasticsearch",
    "Opensearch", "Solr", "Logstash",

    # ── Cloud ─────────────────────────────────────────
    "AWS", "GCP", "Azure", "OVH", "Scaleway",
    "S3", "GCS", "ADLS", "EC2", "Lambda",
    "EMR", "Glue", "Athena", "SageMaker",
    "Dataflow", "Dataproc", "Vertex AI", "BigQuery",
    "Data Factory", "Databricks", "Synapse",

    # ── DevOps & infrastructure ───────────────────────
    "Docker", "Kubernetes", "Helm", "Terraform",
    "Ansible", "Puppet", "Vagrant",
    "CI/CD", "Jenkins", "GitLab CI", "GitHub Actions",
    "CircleCI", "ArgoCD", "Prometheus", "Grafana",
    "Datadog", "New Relic", "ELK", "Jaeger",

    # ── Versioning & collaboration ────────────────────
    "Git", "GitHub", "GitLab", "Bitbucket",
    "Jira", "Confluence", "Notion",

    # ── Visualisation & BI ────────────────────────────
    "Power BI", "PowerBI", "Tableau", "Looker",
    "Metabase", "Superset", "Kibana",
    "QlikView", "QlikSense", "MicroStrategy",
    "Cognos", "SSRS", "Data Studio", "Redash",

    # ── Machine Learning & MLOps ──────────────────────
    "Weights & Biases", "Neptune",
    "DVC", "BentoML", "Seldon", "KFServing",
    "Ray", "Optuna", "Hyperopt", "AutoML",
    "H2O", "DataRobot",

    # ── IA générative & LLM ───────────────────────────
    "LangChain", "LlamaIndex", "OpenAI", "GPT",
    "HuggingFace", "Mistral", "Llama",
    "RAG", "Embeddings", "Vector DB",
    "Pinecone", "Weaviate", "Chroma", "Qdrant",
    "Langsmith", "Ollama",

    # ── Data quality & gouvernance ────────────────────
    "Great Expectations", "Deequ", "Monte Carlo",
    "Atlan", "Collibra", "Alation", "DataHub",
    "Apache Atlas", "OpenMetadata",

    # ── Formats & sérialisation ───────────────────────
    "Parquet", "Avro", "ORC", "JSON", "XML",
    "CSV", "Arrow", "Protobuf",

    # ── Méthodes & pratiques ──────────────────────────
    "ETL", "ELT", "DataOps", "MLOps", "DevOps",
    "Agile", "Scrum", "Kanban", "TDD",
    "RGPD", "Data Mesh", "Data Lakehouse",
    "Data Warehouse", "Data Lake", "Data Vault",
]

# ── Langues pratiquées ────────────────────────────────
LANGUES_PRATIQUEES = [
    "Français", "Francais", "Anglais", "Espagnol", "Allemand"
]

# ── Villes connues ────────────────────────────────
VILLES_CONNUES = [
    # ── Grandes métropoles ────────────────────────────
    "Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux",
    "Nantes", "Lille", "Strasbourg", "Rennes", "Grenoble",
    "Montpellier", "Nice", "Toulon", "Saint-Étienne",
    "Clermont-Ferrand", "Dijon", "Angers", "Nîmes",
    "Aix-en-Provence", "Brest", "Le Havre", "Amiens",
    "Limoges", "Reims", "Tours", "Metz", "Nancy",
    "Orléans", "Rouen", "Caen", "Mulhouse", "Pau",
    "Perpignan", "Valenciennes", "Dunkerque", "Avignon",
    "Poitiers", "La Rochelle", "Bayonne", "Annecy",
    "Chambéry", "Besançon", "Boulogne-Billancourt",
    "Saint-Denis", "Versailles", "Créteil", "Nanterre"
]


# ── Coordonnées GPS des grandes villes ────────────────
COORDS_VILLES = {
    # ── Grandes métropoles ────────────────────────────
    "Paris":                (48.8566,  2.3522),
    "Lyon":                 (45.7640,  4.8357),
    "Marseille":            (43.2965,  5.3698),
    "Toulouse":             (43.6047,  1.4442),
    "Bordeaux":             (44.8378, -0.5792),
    "Nantes":               (47.2184, -1.5536),
    "Lille":                (50.6292,  3.0573),
    "Strasbourg":           (48.5734,  7.7521),
    "Rennes":               (48.1173, -1.6778),
    "Grenoble":             (45.1885,  5.7245),
    "Montpellier":          (43.6108,  3.8767),
    "Nice":                 (43.7102,  7.2620),
    "Toulon":               (43.1242,  5.9280),
    "Saint-Étienne":        (45.4397,  4.3872),
    "Clermont-Ferrand":     (45.7772,  3.0870),
    "Dijon":                (47.3220,  5.0415),
    "Angers":               (47.4784, -0.5632),
    "Nîmes":                (43.8367,  4.3601),
    "Aix-en-Provence":      (43.5297,  5.4474),
    "Brest":                (48.3905, -4.4860),
    "Le Havre":             (49.4938,  0.1077),
    "Amiens":               (49.8941,  2.2958),
    "Limoges":              (45.8336,  1.2611),
    "Reims":                (49.2583,  4.0317),
    "Tours":                (47.3941,  0.6848),
    "Metz":                 (49.1193,  6.1757),
    "Nancy":                (48.6921,  6.1844),
    "Orléans":              (47.9029,  1.9039),
    "Rouen":                (49.4432,  1.0993),
    "Caen":                 (49.1829, -0.3707),
    "Mulhouse":             (47.7508,  7.3359),
    "Pau":                  (43.2951, -0.3708),
    "Perpignan":            (42.6887,  2.8948),
    "Valenciennes":         (50.3589,  3.5234),
    "Dunkerque":            (51.0343,  2.3752),
    "Avignon":              (43.9493,  4.8055),
    "Poitiers":             (46.5802,  0.3404),
    "La Rochelle":          (46.1591, -1.1520),
    "Bayonne":              (43.4929, -1.4748),
    "Annecy":               (45.8992,  6.1294),
    "Chambéry":             (45.5646,  5.9178),
    "Besançon":             (47.2378,  6.0241),
    "Boulogne-Billancourt": (48.8352,  2.2410),
    "Saint-Denis":          (48.9362,  2.3574),
    "Versailles":           (48.8014,  2.1301),
    "Créteil":              (48.7904,  2.4558),
    "Nanterre":             (48.8924,  2.2070),
}

# ── Niveaux de formation (ordre croissant OBLIGATOIRE) ─
NIVEAUX_FORMATION = [
    "CAP", "BEP", "Bac", "Bac+1",
    "Bac+2", "BTS", "DUT", "DEUG",
    "Bac+3", "Licence", "Bachelor", "BUT",
    "Bac+4", "Maîtrise", "Master 1",
    "Bac+5", "Master", "Master 2", "Ingénieur", "DEA", "DESS",
    "Bac+6", "Bac+7", "Bac+8",
    "Doctorat", "PhD", "HDR"
]

# ── Mapping formation → niveau numérique ──────────────
FORMATION_SCORE = {
    "CAP":       1,
    "BEP":       1,
    "Bac":       2,
    "Bac+1":     2,
    "Bac+2":     3,
    "BTS":       3,
    "DUT":       3,
    "DEUG":      3,
    "Bac+3":     4,
    "Licence":   4,
    "Bachelor":  4,
    "BUT":       4,
    "Bac+4":     5,
    "Maîtrise":  5,
    "Master 1":  5,
    "Bac+5":     6,
    "Master":    6,
    "Master 2":  6,
    "Ingénieur": 6,
    "DEA":       6,
    "DESS":      6,
    "Bac+6":     7,
    "Bac+7":     7,
    "Bac+8":     7,
    "Doctorat":  8,
    "PhD":       8,
    "HDR":       9,
    "Non précisé": 0
}
