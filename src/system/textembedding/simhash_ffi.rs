// OMNI SYSTEM LAYER: Text Embedding (Rust)
// FFI for blazingly fast SimHash calculation for document deduplication.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

#[no_mangle]
pub extern "C" fn omni_calculate_simhash(
    text_ptr: *const u8,
    text_len: usize,
    hash_out: *mut u64
) -> i32 {
    if text_ptr.is_null() || hash_out.is_null() {
        return -1; // Omni Error Code: Null pointer
    }

    let text_slice = unsafe { std::slice::from_raw_parts(text_ptr, text_len) };
    let text = match std::str::from_utf8(text_slice) {
        Ok(s) => s,
        Err(_) => return -2, // Omni Error Code: Invalid UTF-8
    };

    let mut v = [0i32; 64];

    for word in text.split_whitespace() {
        let mut hasher = DefaultHasher::new();
        word.hash(&mut hasher);
        let word_hash = hasher.finish();

        for i in 0..64 {
            let bit = (word_hash >> i) & 1;
            if bit == 1 {
                v[i] += 1;
            } else {
                v[i] -= 1;
            }
        }
    }

    let mut final_hash: u64 = 0;
    for i in 0..64 {
        if v[i] > 0 {
            final_hash |= 1 << i;
        }
    }

    unsafe {
        *hash_out = final_hash;
    }

    0 // Success
}
