// moe_expert_encryption.rs — System / Security
// Layer: System / Core — Expert Weight Encryption
//
// In multi-tenant edge deployments, proprietary expert weights (e.g., highly 
// tuned financial experts) must be encrypted at rest. This module provides
// AES-256-GCM encryption/decryption on the fly as weights load into VRAM.

use ring::aead;
use ring::rand::{SystemRandom, SecureRandom};

pub struct ExpertEncryptor {
    key: aead::LessSafeKey,
}

impl ExpertEncryptor {
    /// Initializes with a master key. In production, this comes from a KMS/HSM.
    pub fn new(key_bytes: &[u8; 32]) -> Self {
        let unbound_key = aead::UnboundKey::new(&aead::AES_256_GCM, key_bytes).unwrap();
        let key = aead::LessSafeKey::new(unbound_key);
        println!("[Security] Initialized AES-256-GCM Expert Weight Encryptor.");
        ExpertEncryptor { key }
    }

    /// Generates a random 12-byte nonce
    fn generate_nonce(&self) -> [u8; 12] {
        let rng = SystemRandom::new();
        let mut nonce = [0u8; 12];
        rng.fill(&mut nonce).unwrap();
        nonce
    }

    /// Encrypts a block of weight data
    pub fn encrypt_weights(&self, plaintext: &[u8]) -> Vec<u8> {
        let nonce_bytes = self.generate_nonce();
        let nonce = aead::Nonce::assume_unique_for_key(nonce_bytes);
        
        let mut in_out = plaintext.to_vec();
        // The tag is appended to the end of the ciphertext
        self.key.seal_in_place_append_tag(nonce, aead::Aad::empty(), &mut in_out).unwrap();
        
        // Prepend nonce to ciphertext for storage
        let mut final_payload = nonce_bytes.to_vec();
        final_payload.extend(in_out);
        
        final_payload
    }

    /// Decrypts weights directly before copying to VRAM
    pub fn decrypt_weights(&self, ciphertext_with_nonce: &mut [u8]) -> Result<&[u8], ring::error::Unspecified> {
        if ciphertext_with_nonce.len() < 12 {
            return Err(ring::error::Unspecified);
        }
        
        let mut nonce_bytes = [0u8; 12];
        nonce_bytes.copy_from_slice(&ciphertext_with_nonce[0..12]);
        let nonce = aead::Nonce::assume_unique_for_key(nonce_bytes);
        
        // Decrypt in place (the output will be smaller as the tag is removed)
        let plaintext = self.key.open_in_place(nonce, aead::Aad::empty(), &mut ciphertext_with_nonce[12..])?;
        Ok(plaintext)
    }
}
