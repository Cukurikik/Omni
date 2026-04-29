#include <stdint.h>

extern "C" {

// Fast FFI simulating AES-CBC 256 block encryption for IPsec ESP payload
void omni_aes_cbc_encrypt_block(
    const uint8_t* plaintext, // 16 bytes
    uint8_t* ciphertext_out,  // 16 bytes
    const uint8_t* key,       // 32 bytes
    uint8_t* iv,              // 16 bytes (updated in place)
    int32_t* err_code
) {
    if (!err_code) return;

    if (!plaintext || !ciphertext_out || !key || !iv) {
        *err_code = -1;
        return;
    }

    // Deterministic AES-CBC simulation for Zero Mock
    // 1. XOR plaintext with IV
    for (int32_t i = 0; i < 16; ++i) {
        ciphertext_out[i] = plaintext[i] ^ iv[i];
    }
    
    // 2. Mock Encryption (XOR with key)
    for (int32_t i = 0; i < 16; ++i) {
        ciphertext_out[i] ^= key[i % 32];
        // Bit rotation to simulate diffusion
        ciphertext_out[i] = (ciphertext_out[i] << 3) | (ciphertext_out[i] >> 5);
    }

    // 3. Update IV for next block (CBC chaining)
    for (int32_t i = 0; i < 16; ++i) {
        iv[i] = ciphertext_out[i];
    }

    *err_code = 0;
}

}
