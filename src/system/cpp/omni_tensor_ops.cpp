// OMNI System — C++ AVX Tensor Operations
// High-performance CPU inference kernels

#include <immintrin.h>
#include <vector>
#include <iostream>

extern "C" {
    
    // Compute dot product of two vectors using AVX2
    float omni_avx2_dot_product(const float* a, const float* b, size_t len) {
        float result = 0.0f;
        size_t i = 0;
        
        __m256 sum256 = _mm256_setzero_ps();
        
        for (; i + 7 < len; i += 8) {
            __m256 va = _mm256_loadu_ps(&a[i]);
            __m256 vb = _mm256_loadu_ps(&b[i]);
            sum256 = _mm256_fmadd_ps(va, vb, sum256);
        }
        
        // Horizontal add
        float temp[8];
        _mm256_storeu_ps(temp, sum256);
        for (int j = 0; j < 8; j++) {
            result += temp[j];
        }
        
        // Remainder
        for (; i < len; i++) {
            result += a[i] * b[i];
        }
        
        return result;
    }
}
