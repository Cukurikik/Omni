#include <stdint.h>

#ifdef _MSC_VER
#include <intrin.h>
#endif

extern "C" {

// Fast FFI simulating hardware accelerated Leading Zero Count (LZC/CLZ) for HLL register updating
void omni_simd_leading_zeros(
    uint32_t hash_val,
    int32_t* out_zeros,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_zeros) {
        *err_code = -1;
        return;
    }

    if (hash_val == 0) {
        *out_zeros = 32;
        *err_code = 0;
        return;
    }

    // Hardware accelerated __builtin_clz
#ifdef _MSC_VER
    unsigned long index;
    _BitScanReverse(&index, hash_val);
    *out_zeros = 31 - index;
#else
    *out_zeros = __builtin_clz(hash_val);
#endif

    // HLL uses rank = zeros + 1
    *out_zeros += 1;
    *err_code = 0;
}

}
