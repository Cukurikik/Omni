#include <cstdint>
#include <immintrin.h>

extern "C" {
    // OMNI System Layer - SIMD accelerated character counting for fast CSV parsing
    int32_t count_delimiters_avx2(const uint8_t* data, int32_t length, uint8_t delimiter) {
        if (!data || length <= 0) return 0;
        int32_t count = 0;
        int32_t i = 0;
        __m256i v_delim = _mm256_set1_epi8(delimiter);
        
        for (; i <= length - 32; i += 32) {
            __m256i v_data = _mm256_loadu_si256((const __m256i*)(data + i));
            __m256i v_mask = _mm256_cmpeq_epi8(v_data, v_delim);
            uint32_t mask = _mm256_movemask_epi8(v_mask);
            count += _mm_popcnt_u32(mask);
        }
        
        // Tail processing
        for (; i < length; ++i) {
            if (data[i] == delimiter) count++;
        }
        return count;
    }
}
