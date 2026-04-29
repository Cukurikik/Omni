-- OMNI Language Benchmark Schema — Database/Query Layer
-- Absorbing TOCFL-MultiBench domain data storage patterns.
-- SQL schema for multimodal language proficiency test results.

CREATE TABLE IF NOT EXISTS benchmark_sessions (
    session_id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'zh-TW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_results (
    result_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES benchmark_sessions(session_id),
    question_id TEXT NOT NULL,
    modality TEXT NOT NULL CHECK (modality IN ('text', 'audio', 'image', 'multimodal')),
    predicted_answer INTEGER NOT NULL,
    ground_truth INTEGER NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    proficiency_level TEXT NOT NULL CHECK (proficiency_level IN ('Novice', 'Band-A', 'Band-B', 'Band-C', 'Band-D')),
    is_correct BOOLEAN GENERATED ALWAYS AS (predicted_answer = ground_truth) STORED,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eval_session ON evaluation_results(session_id);
CREATE INDEX IF NOT EXISTS idx_eval_modality ON evaluation_results(modality);

-- Aggregate view for quick reporting
CREATE VIEW IF NOT EXISTS benchmark_summary AS
SELECT
    bs.model_name,
    er.modality,
    COUNT(*) AS total_questions,
    SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END) AS correct_answers,
    ROUND(AVG(CASE WHEN er.is_correct THEN 1.0 ELSE 0.0 END), 4) AS accuracy,
    AVG(er.confidence_score) AS avg_confidence
FROM evaluation_results er
JOIN benchmark_sessions bs ON er.session_id = bs.session_id
GROUP BY bs.model_name, er.modality;
