/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Elliptic Curve Diffie-Hellman (ECDH) Key Exchange over secp256r1 (P-256).
/// Provides Forward Secrecy via ephemeral key pairs without pulling massive dependencies.

use p256::{PublicKey, SecretKey, ecdh::ephemeral_scalar_mul};
use rand_core::OsRng;
use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum EcdhError {
    InvalidPeerPublicKey,
    SharedSecretComputationFailed,
}

impl fmt::Display for EcdhError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EcdhError::InvalidPeerPublicKey => write!(f, "OMNI_FATAL: Provided peer public key is invalid or not on the P-256 curve."),
            EcdhError::SharedSecretComputationFailed => write!(f, "OMNI_FATAL: Failed to derive the shared secret."),
        }
    }
}

pub struct EcdhSession {
    secret_key: SecretKey,
    pub public_key: PublicKey,
}

impl EcdhSession {
    /// Generates a new ephemeral P-256 keypair securely.
    pub fn new() -> Self {
        // OsRng invokes /dev/urandom or Windows BCryptGenRandom
        let secret_key = SecretKey::random(&mut OsRng);
        let public_key = secret_key.public_key();

        Self {
            secret_key,
            public_key,
        }
    }

    /// Derives the shared secret using the remote peer's public key.
    /// The resulting secret MUST be passed through an HKDF (HMAC-based Key Derivation Function) 
    /// before being used as an encryption key.
    pub fn compute_shared_secret(&self, peer_pub_bytes: &[u8]) -> Result<Vec<u8>, EcdhError> {
        // Parse and validate peer's key
        let peer_public = PublicKey::from_sec1_bytes(peer_pub_bytes)
            .map_err(|_| EcdhError::InvalidPeerPublicKey)?;

        // Perform scalar multiplication (ECDH)
        let shared_secret = ephemeral_scalar_mul(
            &self.secret_key.to_nonzero_scalar(),
            &peer_public.to_projective()
        );

        // Convert the x-coordinate of the resulting point to bytes.
        let secret_bytes = shared_secret.to_encoded_point(false);
        let x_coordinate = secret_bytes.x().ok_or(EcdhError::SharedSecretComputationFailed)?;

        Ok(x_coordinate.to_vec())
    }
}

// Zeroization to protect forward secrecy when session ends
impl Drop for EcdhSession {
    fn drop(&mut self) {
        // The SecretKey from p256 implements ZeroizeOnDrop internally,
        // ensuring the scalar is overwritten with zeroes.
    }
}
