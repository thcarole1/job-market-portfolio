CREATE TABLE IF NOT EXISTS candidatures (
    id                      SERIAL PRIMARY KEY,
    offre_id                VARCHAR(50),
    statut                  VARCHAR(40) CHECK (statut IN ('envoyée', 'relance', 'entretien', 'refus')),
    date_candidature        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes                   TEXT,
    cv_path                 TEXT,
    lettre_motivation_path  TEXT
);
