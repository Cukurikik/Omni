#[derive(Debug, PartialEq)]
pub enum IkeError {
    PayloadTooSmall,
    InvalidNextPayload,
    InvalidLength,
}

pub struct IkeHeader {
    pub initiator_spi: u64,
    pub responder_spi: u64,
    pub next_payload: u8,
    pub major_version: u8,
    pub minor_version: u8,
    pub exchange_type: u8,
    pub flags: u8,
    pub message_id: u32,
    pub length: u32,
}

/// Omni Mother System - Security Layer
/// IPSec IKEv2 Payload Validator.
/// Enforces raw byte bounds before passing to the state machine to prevent buffer overflows.
pub struct IkePayloadValidator;

impl IkePayloadValidator {
    /// Strict boundary check for IKEv2 packets.
    pub fn parse_and_validate_header(buffer: &[u8]) -> Result<IkeHeader, IkeError> {
        if buffer.len() < 28 { // IKEv2 Header is strictly 28 bytes
            return Err(IkeError::PayloadTooSmall);
        }

        let initiator_spi = u64::from_be_bytes(buffer[0..8].try_into().unwrap());
        let responder_spi = u64::from_be_bytes(buffer[8..16].try_into().unwrap());
        
        let next_payload = buffer[16];
        let version_byte = buffer[17];
        let major_version = version_byte >> 4;
        let minor_version = version_byte & 0x0F;

        let exchange_type = buffer[18];
        let flags = buffer[19];
        
        let message_id = u32::from_be_bytes(buffer[20..24].try_into().unwrap());
        let length = u32::from_be_bytes(buffer[24..28].try_into().unwrap());

        if (length as usize) > buffer.len() {
            return Err(IkeError::InvalidLength); // Truncated packet
        }

        // IKEv2 Version constraint mapping
        if major_version != 2 {
            // Omni strictly supports IKEv2 natively
            return Err(IkeError::InvalidLength); // Reuse error code for generic failure
        }

        Ok(IkeHeader {
            initiator_spi,
            responder_spi,
            next_payload,
            major_version,
            minor_version,
            exchange_type,
            flags,
            message_id,
            length,
        })
    }
}
