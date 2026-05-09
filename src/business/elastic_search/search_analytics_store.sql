-- @omni-layer Business | @omni-source md-experiments/elastic_transformers | @omni-lang SQL
-- @omni-description Search analytics store: relational schema for query logs,
-- click-through tracking, relevance judgments, and search metrics.

CREATE TABLE IF NOT EXISTS omni_search_indices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    index_type      VARCHAR(50) NOT NULL CHECK(index_type IN ('dense','sparse','hybrid')),
    embedding_model VARCHAR(100),
    total_docs      BIGINT DEFAULT 0,
    avg_doc_length  FLOAT8 DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS omni_search_queries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_id        UUID NOT NULL REFERENCES omni_search_indices(id),
    query_text      TEXT NOT NULL,
    query_vector    FLOAT8[],
    n_results       INT NOT NULL DEFAULT 0,
    latency_ms      FLOAT8 NOT NULL,
    alpha           FLOAT8 DEFAULT 0.7,
    search_type     VARCHAR(20) DEFAULT 'hybrid' CHECK(search_type IN ('dense','sparse','hybrid')),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_index ON omni_search_queries(index_id);
CREATE INDEX IF NOT EXISTS idx_search_time ON omni_search_queries(created_at);

CREATE TABLE IF NOT EXISTS omni_search_clicks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id        UUID NOT NULL REFERENCES omni_search_queries(id),
    doc_id          VARCHAR(255) NOT NULL,
    rank_position   INT NOT NULL,
    relevance_score FLOAT8,
    clicked         BOOLEAN DEFAULT FALSE,
    dwell_time_sec  FLOAT8,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS omni_relevance_judgments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id        UUID NOT NULL REFERENCES omni_search_queries(id),
    doc_id          VARCHAR(255) NOT NULL,
    relevance       INT NOT NULL CHECK(relevance BETWEEN 0 AND 4),
    judge           VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(query_id, doc_id, judge)
);

-- View: search performance metrics
CREATE OR REPLACE VIEW omni_search_metrics AS
SELECT
    i.name AS index_name,
    COUNT(q.id) AS total_queries,
    AVG(q.latency_ms) AS avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY q.latency_ms) AS p95_latency,
    AVG(q.n_results) AS avg_results,
    COUNT(DISTINCT c.query_id) FILTER (WHERE c.clicked) AS queries_with_clicks,
    AVG(CASE WHEN c.clicked THEN c.rank_position END) AS avg_click_position
FROM omni_search_indices i
LEFT JOIN omni_search_queries q ON i.id = q.index_id
LEFT JOIN omni_search_clicks c ON q.id = c.query_id
GROUP BY i.name;
