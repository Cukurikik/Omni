use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce};
use chacha20poly1305::aead::{Aead, KeyInit};
use rand::{rngs::OsRng, RngCore};
use thiserror::Error;

// OMNI Higgsfield - In-Transit Tensor Encryption
// Monadic error handling and memory safe encryption for gradients crossing public networks

#[derive(Error, Debug)]
pub enum EncryptionError {
    #[error("Cipher operation failed")]
    CipherError,
    #[error("Invalid key length")]
    InvalidKey,
}

pub struct TensorEncryptor {
    cipher: ChaCha20Poly1305,
}

impl TensorEncryptor {
    pub fn new(key_bytes: &[u8]) -> Result<Self, EncryptionError> {
        if key_bytes.len() != 32 {
            return Err(EncryptionError::InvalidKey);
        }
        let key = Key::from_slice(key_bytes);
        let cipher = ChaCha20Poly1305::new(key);
        Ok(Self { cipher })
    }

    pub fn encrypt_tensor(&self, plaintext: &[u8]) -> Result<(Vec<u8>, Vec<u8>), EncryptionError> {
        let mut nonce_bytes = [0u8; 12];
        OsRng.fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self.cipher.encrypt(nonce, plaintext)
            .map_err(|_| EncryptionError::CipherError)?;

        Ok((ciphertext, nonce_bytes.to_vec()))
    }

    pub fn decrypt_tensor(&self, ciphertext: &[u8], nonce_bytes: &[u8]) -> Result<Vec<u8>, EncryptionError> {
        if nonce_bytes.len() != 12 {
            return Err(EncryptionError::CipherError);
        }
        let nonce = Nonce::from_slice(nonce_bytes);

        let plaintext = self.cipher.decrypt(nonce, ciphertext)
            .map_err(|_| EncryptionError::CipherError)?;

        Ok(plaintext)
    }
}
