// Unit test: CryptoEngine encrypt/decrypt roundtrip
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_encrypt_decrypt() {
        let e = CryptoEngine::new(CipherType::Aes256Gcm, vec![0u8; 32]).unwrap();
        let enc = e.encrypt(b"hello").unwrap();
        let dec = e.decrypt(&enc).unwrap();
        assert_eq!(dec, b"hello");
    }
}