-- SQL to initialize predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    asset VARCHAR(20) NOT NULL,
    signal VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    predicted_change FLOAT NOT NULL,
    model_version VARCHAR(10) NOT NULL
);
