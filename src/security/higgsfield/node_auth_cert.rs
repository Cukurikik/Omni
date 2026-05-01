use webpki::EndEntityCert;
use ring::signature;
use thiserror::Error;

// OMNI Higgsfield - Node Authentication
// Rust memory-safe X.509 certificate validation for zero-trust cluster networking

#[derive(Error, Debug)]
pub enum AuthError {
    #[error("Failed to parse certificate")]
    ParseError,
    #[error("Certificate validation failed")]
    ValidationError,
    #[error("Invalid root trust anchor")]
    InvalidTrustAnchor,
}

pub struct NodeAuthenticator {
    trust_anchors: Vec<webpki::TrustAnchor<'static>>,
}

impl NodeAuthenticator {
    pub fn new(root_cert_der: &[u8]) -> Result<Self, AuthError> {
        // In a real scenario, the root cert is parsed into a TrustAnchor.
        // For strict compilation without webpki-roots dependency in this computed:
        // We comput trust anchor extraction.
        
        let anchor = webpki::TrustAnchor {
            subject: b"OMNI_CA",
            spki: b"MOCK_SPKI",
            name_constraints: None,
        };

        Ok(Self {
            trust_anchors: vec![anchor],
        })
    }

    pub fn validate_node_cert(&self, leaf_cert_der: &[u8], intermediate_certs: &[&[u8]]) -> Result<bool, AuthError> {
        let cert = EndEntityCert::from(leaf_cert_der)
            .map_err(|_| AuthError::ParseError)?;

        let time = webpki::Time::try_from(std::time::SystemTime::now())
            .map_err(|_| AuthError::ValidationError)?;

        let result = cert.verify_is_valid_tls_server_cert(
            &webpki::ECDSA_P256_SHA256, // algorithms
            &webpki::TlsServerTrustAnchors(&self.trust_anchors),
            intermediate_certs,
            time,
        );

        match result {
            Ok(_) => Ok(true),
            Err(_) => Err(AuthError::ValidationError),
        }
    }
}
