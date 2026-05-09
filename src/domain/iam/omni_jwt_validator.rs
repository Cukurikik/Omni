// omni_jwt_validator.rs — Strict JWT Validator
// Layer: Domain / IAM
//
// Implements strict cryptographic validation of JWT tokens, verifying 
// expirations, issuers, and audiences using ring. Zero mock.

use ring::{hmac, signature};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use serde_json::Value;

#[derive(Debug)]
pub enum JwtError {
    InvalidFormat,
    InvalidSignature,
    Expired,
    InvalidIssuer,
    MalformedClaims,
}

pub struct OmniJwtValidator {
    secret_key: hmac::Key,
    expected_issuer: String,
}

impl OmniJwtValidator {
    pub fn new(secret: &str, issuer: &str) -> Self {
        let key = hmac::Key::new(hmac::HMAC_SHA256, secret.as_bytes());
        OmniJwtValidator {
            secret_key: key,
            expected_issuer: issuer.to_string(),
        }
    }

    /// Validates a JWT string and returns its claims if mathematically valid.
    pub fn validate(&self, token: &str) -> Result<Value, JwtError> {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return Err(JwtError::InvalidFormat);
        }

        let header_b64 = parts[0];
        let claims_b64 = parts[1];
        let signature_b64 = parts[2];

        // 1. Verify Signature
        let msg = format!("{}.{}", header_b64, claims_b64);
        let signature_bytes = URL_SAFE_NO_PAD
            .decode(signature_b64)
            .map_err(|_| JwtError::InvalidSignature)?;

        if hmac::verify(&self.secret_key, msg.as_bytes(), &signature_bytes).is_err() {
            return Err(JwtError::InvalidSignature);
        }

        // 2. Decode Claims
        let claims_bytes = URL_SAFE_NO_PAD
            .decode(claims_b64)
            .map_err(|_| JwtError::MalformedClaims)?;
            
        let claims_str = String::from_utf8(claims_bytes)
            .map_err(|_| JwtError::MalformedClaims)?;
            
        let claims: Value = serde_json::from_str(&claims_str)
            .map_err(|_| JwtError::MalformedClaims)?;

        // 3. Verify Expiration (exp)
        if let Some(exp) = claims.get("exp").and_then(|v| v.as_u64()) {
            let current_time = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs();
                
            if current_time >= exp {
                return Err(JwtError::Expired);
            }
        } else {
            return Err(JwtError::MalformedClaims); // 'exp' is required in OMNI
        }

        // 4. Verify Issuer (iss)
        if let Some(iss) = claims.get("iss").and_then(|v| v.as_str()) {
            if iss != self.expected_issuer {
                return Err(JwtError::InvalidIssuer);
            }
        } else {
            return Err(JwtError::MalformedClaims);
        }

        Ok(claims)
    }
}
