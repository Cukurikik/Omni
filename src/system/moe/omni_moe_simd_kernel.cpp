#include <immintrin.h>
#include <cstdint>
#include <cstddef>

extern "C" void omni_moe_simd_add(float* a, float* b, float* out, size_t n) {
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        __m256 va = _mm256_loadu_ps(&a[i]);
        __m256 vb = _mm256_loadu_ps(&b[i]);
        _mm256_storeu_ps(&out[i], _mm256_add_ps(va, vb));
    }
    for (; i < n; ++i) {
        out[i] = a[i] + b[i];
    }
}
