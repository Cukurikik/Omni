#include <stdint.h>

extern "C" {

// Fast FFI simulating high-speed hardware RNG for probabilistic particle generation
void omni_fast_prng_fill(
    uint64_t seed,
    double* out_buffer,
    int32_t count,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_buffer || count <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic xoshiro256** simulation
    uint64_t state = seed ^ 0x9E3779B97F4A7C15ULL;
    
    for (int32_t i = 0; i < count; i++) {
        state ^= state >> 12;
        state ^= state << 25;
        state ^= state >> 27;
        
        // Convert to double in [0, 1)
        out_buffer[i] = (state >> 11) * 0x1.0p-53;
    }

    *err_code = 0;
}

}
