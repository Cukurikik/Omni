use ring::aead;
use ring::rand::{SystemRandom, SecureRandom};

pub struct OmniCryptoError(&'static str);

pub fn omni_aes256_gcm_encrypt(key: &[u8; 32], plaintext: &[u8], aad: &[u8]) -> Result<Vec<u8>, OmniCryptoError> {
    let unbound_key = aead::UnboundKey::new(&aead::AES_256_GCM, key)
        .map_err(|_| OmniCryptoError("Invalid key length"))?;
    let sealing_key = aead::SealingKey::new(unbound_key, aead::NONCE_LEN);
    
    let rand = SystemRandom::new();
    let mut nonce_bytes = [0u8; aead::NONCE_LEN];
    rand.fill(&mut nonce_bytes).map_err(|_| OmniCryptoError("Failed to generate nonce"))?;
    let nonce = aead::Nonce::assume_unique_for_key(nonce_bytes);
    
    let mut in_out = plaintext.to_vec();
    let aad_data = aead::Aad::from(aad);
    
    sealing_key.seal_in_place_append_tag(nonce, aad_data, &mut in_out)
        .map_err(|_| OmniCryptoError("Encryption failed"))?;
        
    let mut result = nonce_bytes.to_vec();
    result.extend(in_out);
    Ok(result)
}
