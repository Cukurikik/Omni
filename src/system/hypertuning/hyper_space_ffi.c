// OMNI SYSTEM LAYER: Hyperparameter Tuning (C)
// FFI for ultra-fast pseudo-random coordinate sampling in bounded hyper-space.

#include <stdint.h>
#include <stdlib.h>

// XorShift64* PRNG for high-speed uniform generation
uint64_t xorshift64star(uint64_t* state) {
    uint64_t x = *state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    *state = x;
    return x * 0x2545F4914F6CDD1DULL;
}

double rand_uniform(uint64_t* state, double min, double max) {
    uint64_t r = xorshift64star(state);
    double fraction = (double)r / (double)UINT64_MAX;
    return min + fraction * (max - min);
}

// Generates N points in D dimensions bounded by min_bounds and max_bounds
// Caller MUST free the returned pointer using omni_free_hyperspace
int omni_sample_hyperspace(uint64_t seed, int n_points, int dims, const double* min_bounds, const double* max_bounds, double* out_samples) {
    if (!min_bounds || !max_bounds || !out_samples || n_points <= 0 || dims <= 0) {
        return -1; // Omni Error Code
    }

    uint64_t state = seed;
    for (int i = 0; i < n_points; i++) {
        for (int d = 0; d < dims; d++) {
            out_samples[i * dims + d] = rand_uniform(&state, min_bounds[d], max_bounds[d]);
        }
    }

    return 0; // Success
}
