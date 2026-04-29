-- XGrammar query usage limits
-- SQL schema and bound constraints

CREATE TABLE xgrammar_usage (
    tenant_id UUID PRIMARY KEY,
    grammar_compiles INT NOT NULL DEFAULT 0,
    tokens_parsed BIGINT NOT NULL DEFAULT 0,
    
    -- Absolute DB level constraints to prevent overflow/abuse
    CONSTRAINT check_compiles_limit CHECK (grammar_compiles <= 100000),
    CONSTRAINT check_tokens_limit CHECK (tokens_parsed <= 10000000000)
);

CREATE OR REPLACE FUNCTION check_xgrammar_limits(t_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    current_compiles INT;
BEGIN
    SELECT grammar_compiles INTO current_compiles FROM xgrammar_usage WHERE tenant_id = t_id;
    IF current_compiles > 99000 THEN
        RETURN FALSE; -- Approaching limit
    END IF;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
