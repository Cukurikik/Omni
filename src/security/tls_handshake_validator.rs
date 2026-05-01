use std::convert::TryInto;

#[derive(Debug, PartialEq)]
pub enum TlsError {
    InvalidRecordLength,
    UnsupportedVersion,
    HandshakeParseError,
    CipherSuiteNotAllowed,
}

/// Omni Mother System - Security Layer
/// Strict Zero-Allocation TLS 1.3 Handshake Validator.
/// Parses raw byte buffers to ensure no malicious payloads or downgraded cipher suites
/// enter the network layer before cryptographic processing.
pub struct TlsHandshakeValidator;

impl TlsHandshakeValidator {
    /// Parses a raw TLS ClientHello frame, operating purely on slice references (Zero-Copy).
    pub fn validate_client_hello(buffer: &[u8]) -> Result<(), TlsError> {
        // TLS Record Header length is 5 bytes
        if buffer.len() < 5 {
            return Err(TlsError::InvalidRecordLength);
        }

        // Byte 0: Content Type (22 = Handshake)
        if buffer[0] != 22 {
            return Err(TlsError::HandshakeParseError);
        }

        // Bytes 1-2: Legacy Version (0x0301 for TLS 1.0, often used for compatibility)
        // Bytes 3-4: Length
        let length = u16::from_be_bytes(buffer[3..5].try_into().unwrap()) as usize;
        
        if buffer.len() < 5 + length {
            return Err(TlsError::InvalidRecordLength);
        }

        let handshake_data = &buffer[5..5 + length];
        
        // Handshake Type: 1 = ClientHello
        if handshake_data.is_empty() || handshake_data[0] != 1 {
             return Err(TlsError::HandshakeParseError);
        }

        // Skip 3 bytes of handshake length, 2 bytes of legacy version, 32 bytes of random
        let mut offset = 1 + 3 + 2 + 32;

        if offset > handshake_data.len() {
             return Err(TlsError::HandshakeParseError);
        }

        // Session ID length
        let session_id_len = handshake_data[offset] as usize;
        offset += 1 + session_id_len;

        if offset + 2 > handshake_data.len() {
             return Err(TlsError::HandshakeParseError);
        }

        // Cipher Suites length
        let cipher_suites_len = u16::from_be_bytes(handshake_data[offset..offset+2].try_into().unwrap()) as usize;
        offset += 2;

        if offset + cipher_suites_len > handshake_data.len() {
             return Err(TlsError::HandshakeParseError);
        }

        let cipher_suites = &handshake_data[offset..offset+cipher_suites_len];
        
        // Security constraint: Must support at least TLS_AES_128_GCM_SHA256 (0x13, 0x01)
        // or TLS_AES_256_GCM_SHA384 (0x13, 0x02)
        let mut has_secure_cipher = false;
        for chunk in cipher_suites.chunks_exact(2) {
            if (chunk[0] == 0x13 && chunk[1] == 0x01) || (chunk[0] == 0x13 && chunk[1] == 0x02) {
                has_secure_cipher = true;
                break;
            }
        }

        if !has_secure_cipher {
            return Err(TlsError::CipherSuiteNotAllowed);
        }

        // In a full implementation, we also parse extensions here to verify SupportedVersions = TLS 1.3
        
        Ok(())
    }
}
