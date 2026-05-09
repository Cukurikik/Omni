// OMNI System Layer: AVX-512 Math
#include <immintrin.h>

extern "C" void omni_simd_add(float* a, float* b, float* c, size_t len) {
    for (size_t i = 0; i < len; i += 16) {
        __m512 va = _mm512_loadu_ps(&a[i]);
        __m512 vb = _mm512_loadu_ps(&b[i]);
        __m512 vc = _mm512_add_ps(va, vb);
        _mm512_storeu_ps(&c[i], vc);
    }
}
