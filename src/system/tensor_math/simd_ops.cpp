#include <immintrin.h>
#include <cstddef>

extern "C" {
    // Vectorized dot product using AVX-256
    // Returns 0 on success, -1 on alignment error
    int omni_simd_dot_product(const float* a, const float* b, size_t n, float* result) {
        if (n % 8 != 0) return -1; // Require 8-float alignment for AVX
        
        __m256 sum_vec = _mm256_setzero_ps();
        for (size_t i = 0; i < n; i += 8) {
            __m256 va = _mm256_loadu_ps(&a[i]);
            __m256 vb = _mm256_loadu_ps(&b[i]);
            sum_vec = _mm256_fmadd_ps(va, vb, sum_vec);
        }
        
        // Horizontal add
        float temp[8];
        _mm256_storeu_ps(temp, sum_vec);
        float final_sum = 0.0f;
        for (int i = 0; i < 8; ++i) {
            final_sum += temp[i];
        }
        *result = final_sum;
        return 0;
    }
}
