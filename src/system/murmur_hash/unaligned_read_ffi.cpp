#include <stdint.h>

extern "C" {

// Fast FFI simulating unaligned memory reads for MurmurHash core
void omni_unaligned_read32(
    const uint8_t* memory_ptr,
    int32_t offset,
    uint32_t* out_val,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!memory_ptr || !out_val) {
        *err_code = -1;
        return;
    }

    if (offset < 0) {
        *err_code = -2;
        return;
    }

    // Zero mock deterministic simulation of unaligned 32-bit read
    // Safely reads 4 bytes regardless of alignment (simulating x86 behavior)
    uint32_t val = 0;
    val |= ((uint32_t)memory_ptr[offset]);
    val |= ((uint32_t)memory_ptr[offset + 1]) << 8;
    val |= ((uint32_t)memory_ptr[offset + 2]) << 16;
    val |= ((uint32_t)memory_ptr[offset + 3]) << 24;

    *out_val = val;
    *err_code = 0;
}

}
