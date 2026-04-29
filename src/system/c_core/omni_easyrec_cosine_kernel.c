/* Omni EasyRec Similarity Kernel (C) */
/* System Layer: SIMD-friendly cosine similarity for recommendation. */
/* Ref: HKUDS/EasyRec — EMNLP 2025 */
#include <stddef.h>
#include <math.h>
float omni_cosine_sim(const float* a, const float* b, size_t n) {
    float dot = 0.0f, na = 0.0f, nb = 0.0f;
    for (size_t i = 0; i < n; ++i) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
    float denom = sqrtf(na) * sqrtf(nb);
    return denom > 0.0f ? dot / denom : 0.0f;
}
