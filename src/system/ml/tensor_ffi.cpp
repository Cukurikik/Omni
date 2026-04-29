#include <cstdint>
#include <immintrin.h>

extern "C" {

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

// OMNI System Layer FFI export for C# / .NET
// Returns 0 on success, non-zero on failure
EXPORT int process_tensor_f32(const float* input, int size, float* output) {
    if (!input || !output || size <= 0) return 1;

    int i = 0;
    
    // AVX processing loop (processing 8 floats at a time)
    __m256 two = _mm256_set1_ps(2.0f);
    for (; i + 7 < size; i += 8) {
        __m256 in_vec = _mm256_loadu_ps(input + i);
        __m256 out_vec = _mm256_mul_ps(in_vec, two);
        _mm256_storeu_ps(output + i, out_vec);
    }
    
    // Remainder loop
    for (; i < size; ++i) {
        output[i] = input[i] * 2.0f;
    }

    return 0; // Success
}

}
