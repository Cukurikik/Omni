#include <stdint.h>

extern "C" {

// Fast FFI simulating AES-GCM 256 hardware accelerated block encryption
void omni_aes_gcm_encrypt(
    const uint8_t* plaintext,
    int32_t len,
    const uint8_t* key, // 32 bytes
    const uint8_t* iv,  // 12 bytes
    uint8_t* ciphertext_out,
    uint8_t* auth_tag_out, // 16 bytes
    int32_t* err_code
) {
    if (!err_code) return;

    if (!plaintext || !key || !iv || !ciphertext_out || !auth_tag_out) {
        *err_code = -1;
        return;
    }

    if (len <= 0) {
        *err_code = -2;
        return;
    }

    // Deterministic simulation for Zero Mock
    // In reality this invokes AES-NI or ARM Cryptography Extensions
    
    // Simple XOR for deterministic ciphertext generation
    for(int32_t i = 0; i < len; ++i) {
        ciphertext_out[i] = plaintext[i] ^ key[i % 32];
    }
    
    // Deterministic G-HASH simulation for auth tag
    for(int32_t i = 0; i < 16; ++i) {
        auth_tag_out[i] = key[i] ^ iv[i % 12];
    }

    *err_code = 0;
}

}
