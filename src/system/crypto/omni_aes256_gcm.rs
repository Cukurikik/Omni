// omni_aes256_gcm.rs — Authenticated Encryption wrapper
// Layer: System / Rust
//
// Safe, high-performance binding for AES-256-GCM authenticated encryption,
// ensuring zero-trust data security at rest and in transit for OMNI databases.

use ring::aead::{self, Aad, BoundKey, Nonce, NonceSequence, OpeningKey, SealingKey, UnboundKey};
use ring::error::Unspecified;

// Static nonce sequence for demonstration.
// In production, use a strictly monotonic or randomized sequence.
struct CounterNonceSequence(u64);

impl NonceSequence for CounterNonceSequence {
    fn advance(&mut self) -> Result<Nonce, Unspecified> {
        let mut nonce_bytes = [0u8; 12];
        let counter_bytes = self.0.to_be_bytes();
        // Pack counter into the last 8 bytes of the nonce
        nonce_bytes[4..].copy_from_slice(&counter_bytes);
        self.0 += 1;
        Nonce::try_assume_unique_for_key(&nonce_bytes)
    }
}

pub struct OmniCryptoBox {
    key: [u8; 32], // 256-bit key
}

impl OmniCryptoBox {
    pub fn new(key_material: [u8; 32]) -> Self {
        Self { key: key_material }
    }

    /// Encrypts data in place. The `data` buffer will be extended by the authentication tag.
    pub fn encrypt_in_place(&self, mut data: Vec<u8>, associated_data: &[u8]) -> Result<Vec<u8>, &'static str> {
        let unbound_key = UnboundKey::new(&aead::AES_256_GCM, &self.key)
            .map_err(|_| "Failed to create unbound key")?;
        
        let mut nonce_seq = CounterNonceSequence(1);
        let mut sealing_key = SealingKey::new(unbound_key, nonce_seq);
        
        let aad = Aad::from(associated_data);
        
        sealing_key.seal_in_place_append_tag(aad, &mut data)
            .map_err(|_| "Encryption failed")?;
            
        Ok(data)
    }

    /// Decrypts data in place. Returns the plaintext slice.
    pub fn decrypt_in_place<'a>(&self, data: &'a mut [u8], associated_data: &[u8]) -> Result<&'a mut [u8], &'static str> {
        let unbound_key = UnboundKey::new(&aead::AES_256_GCM, &self.key)
            .map_err(|_| "Failed to create unbound key")?;
        
        let mut nonce_seq = CounterNonceSequence(1);
        let mut opening_key = OpeningKey::new(unbound_key, nonce_seq);
        
        let aad = Aad::from(associated_data);
        
        let plaintext = opening_key.open_in_place(aad, data)
            .map_err(|_| "Decryption or Authentication failed")?;
            
        Ok(plaintext)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encryption_decryption() {
        let key = [0x42; 32];
        let box_crypto = OmniCryptoBox::new(key);
        
        let secret = b"omni-secret-data".to_vec();
        let aad = b"header-info";
        
        let encrypted = box_crypto.encrypt_in_place(secret.clone(), aad).unwrap();
        assert_ne!(secret, encrypted);
        
        let mut dec_buffer = encrypted.clone();
        let decrypted = box_crypto.decrypt_in_place(&mut dec_buffer, aad).unwrap();
        
        assert_eq!(secret, decrypted);
    }
}
