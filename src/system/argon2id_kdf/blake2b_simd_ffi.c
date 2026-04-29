#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI simulating BLAKE2b variable length hashing used internally by Argon2
void omni_blake2b_long_simd(
    const uint8_t* in_data,
    int32_t in_len,
    uint8_t* out_hash, // Target output length
    int32_t out_len,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!in_data || !out_hash || in_len <= 0 || out_len <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic simulation
    // Simulating the repeated hashing (H') mechanism of Argon2 for output > 64 bytes
    
    // Simplistic deterministic fill
    for (int32_t i = 0; i < out_len; i++) {
        out_hash[i] = in_data[i % in_len] ^ (uint8_t)i;
    }

    *err_code = 0;
}

}
