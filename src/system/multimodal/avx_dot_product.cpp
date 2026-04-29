#include <immintrin.h>
#include <cstddef>
#include <string>

extern "C" {

struct DotResult {
    int is_success;
    float value;
    int error_code;
};

// Optimizes cosine similarity inner dot product for normalized CLIP vectors
DotResult avx_dot_product(const float* a, const float* b, size_t n) {
    DotResult res = {0, 0.0f, 0};
    if (!a || !b || n == 0) {
        res.error_code = 1;
        return res;
    }

    __m256 sum256 = _mm256_setzero_ps();
    size_t i = 0;
    
    for (; i + 7 < n; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        sum256 = _mm256_add_ps(sum256, _mm256_mul_ps(va, vb));
    }
    
    // Horizontal Add
    __m128 sum128 = _mm_add_ps(_mm256_castps256_ps128(sum256), _mm256_extractf128_ps(sum256, 1));
    sum128 = _mm_add_ps(sum128, _mm_movehl_ps(sum128, sum128));
    sum128 = _mm_add_ss(sum128, _mm_shuffle_ps(sum128, sum128, 0x55));
    
    float total = _mm_cvtss_f32(sum128);
    
    for (; i < n; ++i) {
        total += a[i] * b[i];
    }
    
    res.is_success = 1;
    res.value = total;
    return res;
}

}
