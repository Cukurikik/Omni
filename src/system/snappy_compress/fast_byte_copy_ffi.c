#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI simulating highly optimized byte copying for LZ77 literals and back-references
void omni_fast_byte_copy(
    const uint8_t* src,
    uint8_t* dest,
    int32_t num_bytes,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!src || !dest) {
        *err_code = -1;
        return;
    }

    if (num_bytes <= 0) {
        *err_code = -2;
        return;
    }

    // Zero mock deterministic simulation
    // Snappy relies heavily on 64-bit aligned fast memory copies
    
    // memcpy is heavily optimized by libc (AVX/SIMD)
    memcpy(dest, src, num_bytes);

    *err_code = 0;
}

}
