#include <stdint.h>
#include <stddef.h>

// Simple XOR stream cipher for lightweight ML telemetry encryption
void omni_crypto_xor_cipher(uint8_t* data, size_t length, const uint8_t* key, size_t key_len) {
    if (key_len == 0) return;
    for (size_t i = 0; i < length; i++) {
        data[i] ^= key[i % key_len];
    }
}
