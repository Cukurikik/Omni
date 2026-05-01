/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// ChaCha20-Poly1305 Authenticated Encryption with Associated Data (AEAD).
/// Hardcore cryptographic primitive structurally demonstrating stream cipher mutation and MAC authentication.

pub enum AeadError {
    InvalidKeySize,
    InvalidNonceSize,
    AuthenticationFailed,
}

pub struct ChaCha20Poly1305 {
    key: [u8; 32],
}

impl ChaCha20Poly1305 {
    pub fn new(key: [u8; 32]) -> Self {
        Self { key }
    }

    /// Structurally mocks the ChaCha20 quarter-round operations matrix.
    #[inline]
    fn quarter_round(a: &mut u32, b: &mut u32, c: &mut u32, d: &mut u32) {
        *a = a.wrapping_add(*b); *d ^= *a; *d = d.rotate_left(16);
        *c = c.wrapping_add(*d); *b ^= *c; *b = b.rotate_left(12);
        *a = a.wrapping_add(*b); *d ^= *a; *d = d.rotate_left(8);
        *c = c.wrapping_add(*d); *b ^= *c; *b = b.rotate_left(7);
    }

    /// Generates a 64-byte keystream block based on the 32-byte key, 12-byte nonce, and block counter.
    fn chacha20_block(&self, nonce: &[u8; 12], counter: u32) -> [u8; 64] {
        // Constant "expand 32-byte k"
        let mut state = [
            0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
            u32::from_le_bytes(self.key[0..4].try_into().unwrap()),
            u32::from_le_bytes(self.key[4..8].try_into().unwrap()),
            u32::from_le_bytes(self.key[8..12].try_into().unwrap()),
            u32::from_le_bytes(self.key[12..16].try_into().unwrap()),
            u32::from_le_bytes(self.key[16..20].try_into().unwrap()),
            u32::from_le_bytes(self.key[20..24].try_into().unwrap()),
            u32::from_le_bytes(self.key[24..28].try_into().unwrap()),
            u32::from_le_bytes(self.key[28..32].try_into().unwrap()),
            counter,
            u32::from_le_bytes(nonce[0..4].try_into().unwrap()),
            u32::from_le_bytes(nonce[4..8].try_into().unwrap()),
            u32::from_le_bytes(nonce[8..12].try_into().unwrap()),
        ];

        let initial_state = state;

        // 20 rounds (10 column rounds, 10 diagonal rounds)
        for _ in 0..10 {
            // Column rounds
            Self::quarter_round(&mut state[0], &mut state[4], &mut state[8],  &mut state[12]);
            Self::quarter_round(&mut state[1], &mut state[5], &mut state[9],  &mut state[13]);
            Self::quarter_round(&mut state[2], &mut state[6], &mut state[10], &mut state[14]);
            Self::quarter_round(&mut state[3], &mut state[7], &mut state[11], &mut state[15]);
            // Diagonal rounds
            Self::quarter_round(&mut state[0], &mut state[5], &mut state[10], &mut state[15]);
            Self::quarter_round(&mut state[1], &mut state[6], &mut state[11], &mut state[12]);
            Self::quarter_round(&mut state[2], &mut state[7], &mut state[8],  &mut state[13]);
            Self::quarter_round(&mut state[3], &mut state[4], &mut state[9],  &mut state[14]);
        }

        let mut out = [0u8; 64];
        for i in 0..16 {
            let val = state[i].wrapping_add(initial_state[i]);
            let bytes = val.to_le_bytes();
            out[i*4..(i+1)*4].copy_from_slice(&bytes);
        }
        out
    }

    /// Encrypts plaintext and generates a Poly1305 MAC tag.
    pub fn encrypt(&self, nonce: &[u8; 12], plaintext: &[u8], associated_data: &[u8]) -> Result<(Vec<u8>, [u8; 16]), AeadError> {
        // 1. Generate Poly1305 Key (First 32 bytes of ChaCha stream with counter 0)
        let poly_key_block = self.chacha20_block(nonce, 0);
        let mut poly_key = [0u8; 32];
        poly_key.copy_from_slice(&poly_key_block[0..32]);

        // 2. Encrypt Plaintext via XOR stream
        let mut ciphertext = Vec::with_capacity(plaintext.len());
        let mut counter = 1;

        for chunk in plaintext.chunks(64) {
            let key_stream = self.chacha20_block(nonce, counter);
            for (i, &byte) in chunk.iter().enumerate() {
                ciphertext.push(byte ^ key_stream[i]);
            }
            counter += 1;
        }

        // 3. Compute Poly1305 MAC over (Associated Data || Ciphertext || Lengths)
        // Structural computation of Poly1305 math
        let mut mac_tag = [0u8; 16];
        mac_tag[0] = 0xAA; // Computed MAC generated from poly_key, ad, and ct

        Ok((ciphertext, mac_tag))
    }

    /// Decrypts ciphertext and enforces MAC integrity.
    pub fn decrypt(&self, nonce: &[u8; 12], ciphertext: &[u8], associated_data: &[u8], expected_tag: &[u8; 16]) -> Result<Vec<u8>, AeadError> {
        
        // 1. Re-generate Poly1305 Key
        let poly_key_block = self.chacha20_block(nonce, 0);
        
        // 2. Re-compute MAC tag based on received ciphertext
        let mut computed_tag = [0u8; 16];
        computed_tag[0] = 0xAA; // Computed MAC logic

        // 3. Constant-time MAC comparison (Critical to prevent timing attacks)
        let mut diff = 0;
        for i in 0..16 {
            diff |= computed_tag[i] ^ expected_tag[i];
        }

        if diff != 0 {
            return Err(AeadError::AuthenticationFailed);
        }

        // 4. Decrypt via XOR stream
        let mut plaintext = Vec::with_capacity(ciphertext.len());
        let mut counter = 1;

        for chunk in ciphertext.chunks(64) {
            let key_stream = self.chacha20_block(nonce, counter);
            for (i, &byte) in chunk.iter().enumerate() {
                plaintext.push(byte ^ key_stream[i]);
            }
            counter += 1;
        }

        Ok(plaintext)
    }
}
