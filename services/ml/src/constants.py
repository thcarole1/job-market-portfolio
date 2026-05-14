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

# ============================================================
# À AJOUTER dans services/ml/src/constants.py
# à la suite de COMPETENCES_CONNUES existant
# ============================================================

SOFT_SKILLS_REFERENCES: dict[str, list[str]] = {

    "autonomie": [
        "capacité à travailler de manière autonome",
        "savoir travailler en autonomie",
        "être autonome dans ses missions",
        "gestion autonome des tâches",
        "prise d'initiative et autonomie",
        "capable de s'organiser seul",
        "travailler sans supervision constante",
        "force de proposition et autonome",
        "gérer ses priorités de façon indépendante",
        "sens de l'autonomie et de la responsabilité",
        "aptitude à travailler de façon indépendante",
        "autoorganisation et autonomie professionnelle",
        "esprit d'initiative fort",
        "capable de mener ses projets en toute indépendance",
        "autonomie dans la gestion des projets techniques",
        "savoir s'auto-former et progresser seul",
        "prise en charge complète des missions sans encadrement rapproché",
        "capacité à avancer sans avoir besoin de directives constantes",
        "proactif et autonome",
        "capable de définir ses propres objectifs",
    ],

    "travail_en_equipe": [
        "travailler en équipe",
        "esprit d'équipe indispensable",
        "capacité à collaborer avec des équipes pluridisciplinaires",
        "sens du collectif",
        "aptitude à travailler en collaboration",
        "goût pour le travail en équipe",
        "savoir s'intégrer dans une équipe",
        "capacité à coopérer avec différents interlocuteurs",
        "travail en mode projet avec des équipes transverses",
        "aisance relationnelle et esprit collaboratif",
        "volonté de partager ses connaissances",
        "contribuer à la dynamique d'équipe",
        "sens de l'entraide et de la solidarité professionnelle",
        "travailler en synergie avec les autres membres",
        "capacité à fédérer autour d'un projet",
        "collaboration étroite avec les équipes métier",
        "intégration facile dans une équipe existante",
        "capacité à travailler avec des profils variés",
        "ouverture aux autres et sens du partage",
        "développer des relations professionnelles constructives",
    ],

    "communication": [
        "excellentes capacités de communication",
        "savoir communiquer clairement à l'oral et à l'écrit",
        "aptitude à vulgariser des sujets techniques",
        "capacité à présenter des résultats à des non-techniciens",
        "aisance à l'oral en présentation",
        "rédaction de documentation claire",
        "capacité à expliquer des concepts complexes simplement",
        "communiquer efficacement avec les équipes métier",
        "adapter son discours à son interlocuteur",
        "sens de la pédagogie",
        "capacité d'écoute active",
        "savoir reformuler et synthétiser",
        "aisance en communication écrite",
        "rédiger des comptes-rendus et rapports clairs",
        "facilité à animer des réunions",
        "capacité à pitcher et convaincre",
        "qualités rédactionnelles reconnues",
        "clarté dans la transmission des informations",
        "savoir poser les bonnes questions",
        "communication fluide avec les parties prenantes",
    ],

    "rigueur": [
        "faire preuve de rigueur",
        "sens du détail et de la précision",
        "minutieux et organisé",
        "capacité à produire un travail de qualité",
        "exigence envers soi-même",
        "respect des procédures et des standards",
        "souci constant de la qualité",
        "attention portée aux détails",
        "rigueur méthodologique",
        "capacité à documenter son travail soigneusement",
        "travail soigné et structuré",
        "respect des délais et des engagements",
        "capacité à vérifier et valider son travail",
        "fiabilité dans les livrables produits",
        "sens de la qualité et de la rigueur",
        "approche méthodique et structurée",
        "organisation rigoureuse",
        "soin apporté à chaque tâche",
        "capacité à travailler avec précision sous contrainte",
        "perfectionnisme constructif",
    ],

    "curiosite": [
        "curiosité intellectuelle",
        "goût pour l'apprentissage continu",
        "veille technologique active",
        "envie d'apprendre de nouveaux outils",
        "intérêt pour les nouvelles technologies",
        "passion pour l'innovation",
        "capacité à se former rapidement",
        "soif d'apprendre",
        "ouverture à de nouvelles méthodes",
        "dynamisme et désir de progresser",
        "capacité d'adaptation aux évolutions technologiques",
        "enthousiasme pour relever de nouveaux défis",
        "intérêt pour les sujets data et intelligence artificielle",
        "curiosité naturelle pour les problèmes complexes",
        "force de proposition sur de nouvelles approches",
        "proactivité dans la recherche de solutions innovantes",
        "se tenir informé des tendances du secteur",
        "participer à des conférences ou communautés tech",
        "aimer expérimenter et tester de nouvelles idées",
        "culture de l'amélioration continue",
    ],

    "gestion_du_stress": [
        "capacité à travailler sous pression",
        "résistance au stress",
        "gérer les situations d'urgence avec calme",
        "maintenir la qualité de travail malgré les délais serrés",
        "capacité à prioriser en situation de crise",
        "sang-froid face aux imprévus",
        "réactivité et gestion des priorités",
        "aptitude à gérer plusieurs sujets en parallèle",
        "garder la tête froide en environnement exigeant",
        "gestion efficace du stress et des délais",
        "capacité à s'adapter rapidement aux changements",
        "résilience face aux obstacles",
        "maintenir sa concentration en environnement agité",
        "capacité à rester efficace sous pression",
        "maîtrise de soi en situation complexe",
        "gérer les conflits de priorités avec sérénité",
        "organisation dans un contexte de forte sollicitation",
        "flexibilité face aux changements de périmètre",
        "capacité à rebondir rapidement après un obstacle",
        "travailler sereinement dans un environnement dynamique",
    ],

    "sens_du_resultat": [
        "orienté résultats",
        "sens des responsabilités et des objectifs",
        "capacité à livrer dans les délais",
        "focus sur la valeur ajoutée",
        "esprit de performance",
        "atteindre les objectifs fixés",
        "sens de l'efficacité opérationnelle",
        "capacité à prioriser selon l'impact",
        "volonté de contribuer concrètement aux résultats",
        "mesurer l'impact de son travail",
        "sens du service et satisfaction client",
        "engagement dans la réussite du projet",
        "capacité à transformer les problèmes en solutions",
        "orientation satisfaction utilisateur",
        "produire des livrables de qualité dans les temps",
        "esprit pragmatique et efficace",
        "chercher l'impact plutôt que la perfection théorique",
        "piloter ses missions par les résultats",
        "sens des priorités et de l'essentiel",
        "capacité à finir ce qu'on commence",
    ],

    "adaptabilite": [
        "capacité d'adaptation",
        "flexibilité et agilité",
        "s'adapter rapidement à de nouveaux environnements",
        "polyvalence",
        "capacité à changer de contexte rapidement",
        "aisance dans les environnements en évolution",
        "ouverture au changement",
        "savoir pivoter face à de nouvelles contraintes",
        "aptitude à évoluer dans un contexte incertain",
        "agilité dans les méthodes de travail",
        "capacité à intégrer rapidement de nouvelles pratiques",
        "s'adapter aux besoins du projet",
        "polyvalence technique et fonctionnelle",
        "travailler dans un environnement en forte croissance",
        "capacité à changer de priorité rapidement",
        "ouverture d'esprit face aux nouvelles façons de travailler",
        "aimer les environnements dynamiques et changeants",
        "s'épanouir dans l'ambiguïté et l'incertitude",
        "agilité intellectuelle",
        "capacité à apprendre sur le tas",
    ],

    "fiabilite": [
        "livrer un travail fiable et de qualité constante",
        "respecter ses engagements",
        "être quelqu'un sur qui on peut compter",
        "sens de la responsabilité",
        "tenir ses délais",
        "produire des résultats reproductibles",
        "maintenir la qualité de ses livrables dans le temps",
        "être digne de confiance dans ses missions",
        "s'assurer de la justesse des résultats produits",
        "ne pas laisser des sujets en suspens",
        "prévenir en cas de blocage ou de retard",
        "assurer la continuité de service",
        "fiabilité dans les engagements pris",
        "sérieux et implication dans les tâches confiées",
        "capacité à maintenir un niveau de qualité constant",
        "respecter les règles et les processus en place",
        "sens du devoir et du travail bien fait",
        "être garant de la qualité des données produites",
        "assurer la traçabilité de son travail",
        "s'assurer que les systèmes fonctionnent correctement",
    ],

    "sens_critique": [
        "esprit critique et analytique",
        "capacité à remettre en question les approches",
        "recul sur les données et les résultats",
        "ne pas accepter un résultat sans le vérifier",
        "questionner les hypothèses de départ",
        "détecter les incohérences et les anomalies",
        "capacité d'analyse approfondie",
        "esprit de synthèse et de recul",
        "aptitude à identifier les problèmes en amont",
        "rigueur dans l'interprétation des données",
        "capacité à challenger les modèles et les méthodes",
        "sens de l'analyse critique des résultats",
        "ne pas se contenter de la première solution venue",
        "capacité à évaluer la pertinence d'une approche",
        "regard critique sur sa propre production",
        "chercher à comprendre le pourquoi des résultats",
        "aptitude à distinguer corrélation et causalité",
        "capacité à identifier les biais dans les données",
        "remettre en question les évidences",
        "cultiver le doute constructif",
    ],
}

SOFT_SKILLS_CATEGORIES: dict[str, list[str]] = {
    "Comportement professionnel": [
        "autonomie", "rigueur", "fiabilite",
        "sens_du_resultat", "adaptabilite", "gestion_du_stress",
    ],
    "Relation aux autres": ["travail_en_equipe", "communication"],
    "Développement personnel": ["curiosite", "sens_critique"],
}

SOFT_SKILLS_LABELS_FR: dict[str, str] = {
    "autonomie": "Autonomie",
    "travail_en_equipe": "Travail en équipe",
    "communication": "Communication",
    "rigueur": "Rigueur",
    "curiosite": "Curiosité",
    "gestion_du_stress": "Gestion du stress",
    "sens_du_resultat": "Sens du résultat",
    "adaptabilite": "Adaptabilité",
    "fiabilite": "Fiabilité",
    "sens_critique": "Sens critique",
}
