// ============================================================
// ⚡ omni-types/system/uuid.rs — Native UUID Generator
// ============================================================

use std::time::{SystemTime, UNIX_EPOCH};

#[repr(C)]
pub struct OmniUUID {
    pub bytes: [u8; 16],
}

extern "C" {
    fn get_random_bytes(buffer: *mut u8, len: usize);
}

// Pseudo-random fallback if get_random_bytes is not available
fn xorshift_seed() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64
}

#[no_mangle]
pub unsafe extern "C" fn omni_uuid_v4() -> OmniUUID {
    let mut bytes = [0u8; 16];
    
    // Asumsikan syscall crypto OMNI tersedia:
    // get_random_bytes(bytes.as_mut_ptr(), 16);
    
    // Simulasi fallback UUIDv4
    let seed = xorshift_seed();
    for i in 0..16 {
        bytes[i] = ((seed >> (i * 4)) & 0xFF) as u8;
    }
    
    // Set version 4 and variant
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;

    OmniUUID { bytes }
}
