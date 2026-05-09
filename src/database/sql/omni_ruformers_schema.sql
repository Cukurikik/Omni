-- OMNI Framework PostgreSQL Schema for Ruformers Classification Results

CREATE SCHEMA IF NOT EXISTS omni_nlp;

CREATE TYPE omni_nlp.sentiment_label AS ENUM ('Positive', 'Neutral', 'Negative', 'Unknown');

CREATE TABLE IF NOT EXISTS omni_nlp.ruformers_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(255) NOT NULL,
    text_snippet TEXT NOT NULL,
    predicted_sentiment omni_nlp.sentiment_label NOT NULL,
    confidence_score NUMERIC(5, 4) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ruformers_doc_id ON omni_nlp.ruformers_results(document_id);
CREATE INDEX idx_ruformers_sentiment ON omni_nlp.ruformers_results(predicted_sentiment);

-- Add comment for OMNI Data Catalog
COMMENT ON TABLE omni_nlp.ruformers_results IS 'Stores sentiment analysis results from the Russian NLP Ruformers pipeline';
