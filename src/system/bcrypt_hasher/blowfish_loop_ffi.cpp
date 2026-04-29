#include <stdint.h>

extern "C" {

// Fast FFI simulating the innermost 64-bit Blowfish encryption block loop
void omni_blowfish_encrypt_block(
    uint32_t* left_half,
    uint32_t* right_half,
    const uint32_t* p_array, // 18 elements
    int32_t* err_code
) {
    if (!err_code) return;

    if (!left_half || !right_half || !p_array) {
        *err_code = -1;
        return;
    }

    uint32_t L = *left_half;
    uint32_t R = *right_half;

    // Feistel network deterministic mock (16 rounds)
    for (int i = 0; i < 16; ++i) {
        L ^= p_array[i];
        // Mock F function: simple rotation and add
        uint32_t F = (L << 4) | (L >> 28);
        F += 0x12345678;
        R ^= F;
        
        // Swap L and R
        uint32_t temp = L;
        L = R;
        R = temp;
    }

    // Final swap undo and post-whitening
    uint32_t temp = L;
    L = R;
    R = temp;

    R ^= p_array[16];
    L ^= p_array[17];

    *left_half = L;
    *right_half = R;
    *err_code = 0;
}

}
