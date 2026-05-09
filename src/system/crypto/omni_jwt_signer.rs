// omni_jwt_signer.rs — High-Speed JWT Signer
// Layer: System / Rust
//
// Rust utility utilizing the ring crate for extremely fast, secure 
// EdDSA or HMAC signing of JSON Web Tokens, callable via FFI by C# and Ruby.

use ring::{hmac, rand};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use serde_json::json;

pub struct OmniJwtSigner {
    key: hmac::Key,
}

impl OmniJwtSigner {
    pub fn new(secret: &[u8]) -> Self {
        let key = hmac::Key::new(hmac::HMAC_SHA256, secret);
        Self { key }
    }

    /// Generates a valid JWT with the provided payload claims.
    pub fn sign_token(&self, subject: &str, role: &str, exp_timestamp: u64) -> String {
        let header = json!({
            "alg": "HS256",
            "typ": "JWT"
        });
        
        let payload = json!({
            "sub": subject,
            "role": role,
            "exp": exp_timestamp
        });

        let header_b64 = URL_SAFE_NO_PAD.encode(header.to_string().as_bytes());
        let payload_b64 = URL_SAFE_NO_PAD.encode(payload.to_string().as_bytes());

        let message = format!("{}.{}", header_b64, payload_b64);
        
        let tag = hmac::sign(&self.key, message.as_bytes());
        let signature_b64 = URL_SAFE_NO_PAD.encode(tag.as_ref());

        format!("{}.{}", message, signature_b64)
    }

    /// Verifies a JWT and returns true if the signature is valid.
    pub fn verify_token(&self, token: &str) -> bool {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return false;
        }

        let message = format!("{}.{}", parts[0], parts[1]);
        
        let signature_bytes = match URL_SAFE_NO_PAD.decode(parts[2]) {
            Ok(b) => b,
            Err(_) => return false,
        };

        hmac::verify(&self.key, message.as_bytes(), &signature_bytes).is_ok()
    }
}
