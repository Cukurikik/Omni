-- @omni-domain Business Layer (OmniQuant Audit)
CREATE TABLE IF NOT EXISTS quantization_audit (id SERIAL PRIMARY KEY, model_name VARCHAR(255) NOT NULL, bits INT NOT NULL CHECK (bits IN (2,3,4,8)), scale DOUBLE PRECISION, zero_point INT, mse_before DOUBLE PRECISION, mse_after DOUBLE PRECISION, created_at TIMESTAMP DEFAULT NOW());
CREATE OR REPLACE FUNCTION audit_quantization() RETURNS TRIGGER AS $$ BEGIN INSERT INTO quantization_audit(model_name, bits, scale, zero_point) VALUES (NEW.model_name, NEW.bits, NEW.scale, NEW.zero_point); RETURN NEW; END; $$ LANGUAGE plpgsql;
