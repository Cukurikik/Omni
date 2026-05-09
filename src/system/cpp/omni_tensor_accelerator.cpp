#include <immintrin.h>
#include <cstddef>
#include <vector>
#include <stdexcept>

class OmniTensorAccelerator {
public:
    // AVX-512 accelerated dot product for transformer inference
    static float dot_product_avx512(const float* a, const float* b, size_t n) {
        if (n % 16 != 0) {
            throw std::invalid_argument("Array size must be a multiple of 16 for AVX-512.");
        }
        
        __m512 sum_vec = _mm512_setzero_ps();
        
        for (size_t i = 0; i < n; i += 16) {
            __m512 vec_a = _mm512_loadu_ps(&a[i]);
            __m512 vec_b = _mm512_loadu_ps(&b[i]);
            sum_vec = _mm512_fmadd_ps(vec_a, vec_b, sum_vec);
        }
        
        return _mm512_reduce_add_ps(sum_vec);
    }
};
