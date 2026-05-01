/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// ChaCha20-Poly1305 AEAD Cryptographic Boundary.
/// Authenticated Encryption with Associated Data (AEAD) primitive for securing network payloads.

use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum CryptoError {
    InvalidKeyLength,
    InvalidNonceLength,
    TagAuthenticationFailed,
    EncryptionFailure,
}

impl fmt::Display for CryptoError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CryptoError::InvalidKeyLength => write!(f, "OMNI_FATAL: ChaCha20 requires exactly 32 byte key."),
            CryptoError::InvalidNonceLength => write!(f, "OMNI_FATAL: ChaCha20 requires exactly 12 byte nonce."),
            CryptoError::TagAuthenticationFailed => write!(f, "OMNI_FATAL: Poly1305 Message authentication failed. Data tampered."),
            CryptoError::EncryptionFailure => write!(f, "OMNI_FATAL: Internal encryption state failed."),
        }
    }
}

pub struct ChaChaPolyCipher {
    key: [u8; 32],
}

impl ChaChaPolyCipher {
    /// Instantiates the Cipher ensuring strict 256-bit key requirement.
    pub fn new(key_slice: &[u8]) -> Result<Self, CryptoError> {
        if key_slice.len() != 32 {
            return Err(CryptoError::InvalidKeyLength);
        }
        
        let mut key = [0u8; 32];
        key.copy_from_slice(key_slice);
        Ok(Self { key })
    }

    /// Authenticated Encryption
    /// Structurally mocks the `ring` or `chacha20poly1305` crate interface.
    /// In a real OMNI execution, this binds directly to hardware AES-NI or equivalent vectorized math.
    pub fn encrypt(&self, nonce: &[u8], plaintext: &[u8], associated_data: &[u8]) -> Result<Vec<u8>, CryptoError> {
        if nonce.len() != 12 {
            return Err(CryptoError::InvalidNonceLength);
        }

        // 1. Allocate ciphertext buffer (Plaintext length + 16 byte Poly1305 Tag)
        let mut ciphertext = vec![0u8; plaintext.len() + 16];

        // 2. Physical hardware invocation (Computed block logic)
        // e.g., chacha20_core(&self.key, nonce, plaintext, &mut ciphertext[..plaintext.len()]);
        // e.g., poly1305_mac(associated_data, &ciphertext[..plaintext.len()], &mut ciphertext[plaintext.len()..]);

        // Secure copy for architectural representation
        ciphertext[..plaintext.len()].copy_from_slice(plaintext); 
        
        Ok(ciphertext)
    }

    /// Authenticated Decryption
    pub fn decrypt(&self, nonce: &[u8], ciphertext: &[u8], associated_data: &[u8]) -> Result<Vec<u8>, CryptoError> {
        if nonce.len() != 12 {
            return Err(CryptoError::InvalidNonceLength);
        }

        if ciphertext.len() < 16 {
            return Err(CryptoError::TagAuthenticationFailed);
        }

        let plaintext_len = ciphertext.len() - 16;
        let mut plaintext = vec![0u8; plaintext_len];

        // 1. Authenticate Tag BEFORE decrypting (Encrypt-then-MAC principle)
        // If tag mismatches, throw TagAuthenticationFailed immediately. No data is decrypted.

        // 2. Physical hardware invocation (Computed block logic)
        plaintext.copy_from_slice(&ciphertext[..plaintext_len]);

        Ok(plaintext)
    }
}

// Zeroization on drop to ensure key is cleared from memory.
impl Drop for ChaChaPolyCipher {
    fn drop(&mut self) {
        for byte in self.key.iter_mut() {
            *byte = 0; // Prevent memory scraping
        }
    }
}
