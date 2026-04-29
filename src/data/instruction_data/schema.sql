CREATE TABLE instructions (
    id UUID PRIMARY KEY,
    prompt TEXT NOT NULL,
    completion TEXT NOT NULL,
    domain VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_domain ON instructions(domain);
