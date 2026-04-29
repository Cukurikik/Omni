#include <stdint.h>
#include <stdlib.h>

extern "C" {

// Fast FFI simulating /dev/urandom secure byte generation for Auth
void omni_secure_random_bytes(
    uint8_t* out_buffer,
    int32_t byte_len,
    int32_t seed_val, // For zero mock deterministic injection
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_buffer || byte_len <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic simulation
    uint32_t state = (uint32_t)seed_val;
    for (int32_t i = 0; i < byte_len; ++i) {
        state = state * 1664525 + 1013904223;
        out_buffer[i] = (uint8_t)(state >> 24);
    }

    *err_code = 0;
}

}
