// OMNI SYSTEM LAYER: Financial DataFrame (C++)
// FFI for ultra-fast columnar memory alignment and zero-copy slicing.

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <immintrin.h>

extern "C" {

    struct OmniColumnView {
        double* data_ptr;
        size_t length;
    };

    // Aligns a column of doubles to 32-byte boundary for AVX instructions
    OmniColumnView omni_alloc_aligned_column(size_t length) {
        void* ptr = nullptr;
        // POSIX memalign equivalent, or simply malloc if aligned_alloc is unavailable
        // We use aligned_alloc for C++17 compatibility.
        size_t alignment = 32;
        size_t size = length * sizeof(double);
        
        // Ensure size is a multiple of alignment
        if (size % alignment != 0) {
            size += alignment - (size % alignment);
        }

#ifdef _WIN32
        ptr = _aligned_malloc(size, alignment);
#else
        ptr = aligned_alloc(alignment, size);
#endif

        if (ptr) {
            std::memset(ptr, 0, size);
        }

        return { static_cast<double*>(ptr), length };
    }

    void omni_free_aligned_column(OmniColumnView col) {
        if (col.data_ptr) {
#ifdef _WIN32
            _aligned_free(col.data_ptr);
#else
            free(col.data_ptr);
#endif
        }
    }

    // Fast SIMD-based addition of two columns
    int omni_simd_add_columns(const double* col1, const double* col2, double* out, size_t length) {
        if (!col1 || !col2 || !out) return -1;

        size_t i = 0;
#ifdef __AVX__
        for (; i + 4 <= length; i += 4) {
            __m256d a = _mm256_loadu_pd(&col1[i]);
            __m256d b = _mm256_loadu_pd(&col2[i]);
            __m256d c = _mm256_add_pd(a, b);
            _mm256_storeu_pd(&out[i], c);
        }
#endif
        // Remainder
        for (; i < length; ++i) {
            out[i] = col1[i] + col2[i];
        }

        return 0; // Success
    }
}
