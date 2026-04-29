#include <immintrin.h>
#include <stddef.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

// Struct for OMNI monadic error handling in C
typedef struct {
    int is_success;
    float value;
    int error_code; // 0=None, 1=NullPointer, 2=DimensionMismatch
} DistanceResult;

DistanceResult simd_euclidean_distance(const float* a, const float* b, size_t n) {
    DistanceResult res = {0, 0.0f, 0};
    
    if (a == NULL || b == NULL) {
        res.error_code = 1;
        return res;
    }
    
    __m256 sum256 = _mm256_setzero_ps();
    size_t i = 0;
    
    // Unroll by 8 (AVX 256-bit registers hold 8 floats)
    for (; i + 7 < n; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        __m256 diff = _mm256_sub_ps(va, vb);
        __m256 sq = _mm256_mul_ps(diff, diff);
        sum256 = _mm256_add_ps(sum256, sq);
    }
    
    // Horizontal addition for AVX
    __m128 sum128 = _mm_add_ps(_mm256_castps256_ps128(sum256), _mm256_extractf128_ps(sum256, 1));
    sum128 = _mm_add_ps(sum128, _mm_movehl_ps(sum128, sum128));
    sum128 = _mm_add_ss(sum128, _mm_shuffle_ps(sum128, sum128, 0x55));
    
    float total = _mm_cvtss_f32(sum128);
    
    // Remainder loop
    for (; i < n; ++i) {
        float d = a[i] - b[i];
        total += d * d;
    }
    
    res.is_success = 1;
    res.value = sqrtf(total);
    return res;
}

DistanceResult simd_cosine_similarity(const float* a, const float* b, size_t n) {
    DistanceResult res = {0, 0.0f, 0};
    if (a == NULL || b == NULL) { res.error_code = 1; return res; }
    
    __m256 dot256 = _mm256_setzero_ps();
    __m256 normA256 = _mm256_setzero_ps();
    __m256 normB256 = _mm256_setzero_ps();
    
    size_t i = 0;
    for (; i + 7 < n; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        
        dot256 = _mm256_add_ps(dot256, _mm256_mul_ps(va, vb));
        normA256 = _mm256_add_ps(normA256, _mm256_mul_ps(va, va));
        normB256 = _mm256_add_ps(normB256, _mm256_mul_ps(vb, vb));
    }
    
    // Extract dot, normA, normB (horizontal add omitted for brevity, logic identical to above)
    float dot = 0, normA = 0, normB = 0;
    float arrDot[8], arrA[8], arrB[8];
    _mm256_storeu_ps(arrDot, dot256);
    _mm256_storeu_ps(arrA, normA256);
    _mm256_storeu_ps(arrB, normB256);
    
    for (int j=0; j<8; j++) { dot += arrDot[j]; normA += arrA[j]; normB += arrB[j]; }
    
    for (; i < n; ++i) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    
    if (normA == 0.0f || normB == 0.0f) {
        res.is_success = 1; 
        res.value = 0.0f;
        return res;
    }
    
    res.is_success = 1;
    res.value = dot / (sqrtf(normA) * sqrtf(normB));
    return res;
}

#ifdef __cplusplus
}
#endif
