/*
 * omni_chacha20.c — ChaCha20 Symmetric Stream Cipher
 * Layer: System / Crypto
 * Inspired by: OpenSSL / libsodium
 *
 * Implements the core ChaCha20 block function and stream XORing.
 * Designed for extreme performance on platforms lacking hardware AES instructions
 * (like mobile devices and IoT microcontrollers). Zero mock.
 */

#include <stdint.h>
#include <string.h>

#define ROTL32(v, n) (((v) << (n)) | ((v) >> (32 - (n))))

static void chacha20_quarter_round(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d) {
    *a += *b; *d = ROTL32(*d ^ *a, 16);
    *c += *d; *b = ROTL32(*b ^ *c, 12);
    *a += *b; *d = ROTL32(*d ^ *a, 8);
    *c += *d; *b = ROTL32(*b ^ *c, 7);
}

static void chacha20_block(uint32_t state[16], uint8_t stream[64]) {
    uint32_t working_state[16];
    memcpy(working_state, state, 64);

    for (int i = 0; i < 10; i++) {
        // Column rounds
        chacha20_quarter_round(&working_state[0], &working_state[4], &working_state[8],  &working_state[12]);
        chacha20_quarter_round(&working_state[1], &working_state[5], &working_state[9],  &working_state[13]);
        chacha20_quarter_round(&working_state[2], &working_state[6], &working_state[10], &working_state[14]);
        chacha20_quarter_round(&working_state[3], &working_state[7], &working_state[11], &working_state[15]);
        
        // Diagonal rounds
        chacha20_quarter_round(&working_state[0], &working_state[5], &working_state[10], &working_state[15]);
        chacha20_quarter_round(&working_state[1], &working_state[6], &working_state[11], &working_state[12]);
        chacha20_quarter_round(&working_state[2], &working_state[7], &working_state[8],  &working_state[13]);
        chacha20_quarter_round(&working_state[3], &working_state[4], &working_state[9],  &working_state[14]);
    }

    // Add working state back to original state
    for (int i = 0; i < 16; i++) {
        uint32_t sum = working_state[i] + state[i];
        
        // Serialize little-endian
        stream[i*4 + 0] = (sum >> 0)  & 0xFF;
        stream[i*4 + 1] = (sum >> 8)  & 0xFF;
        stream[i*4 + 2] = (sum >> 16) & 0xFF;
        stream[i*4 + 3] = (sum >> 24) & 0xFF;
    }
}

// Main encryption/decryption function (XOR stream)
void omni_chacha20_crypt(
    const uint8_t key[32], 
    const uint8_t nonce[12], 
    uint32_t counter, 
    const uint8_t *in, 
    uint8_t *out, 
    size_t length
) {
    uint32_t state[16];

    // Magic constants: "expand 32-byte k"
    state[0] = 0x61707865;
    state[1] = 0x3320646e;
    state[2] = 0x79622d32;
    state[3] = 0x6b206574;

    // Load key (little-endian)
    for (int i = 0; i < 8; i++) {
        state[4 + i] = (key[i*4 + 0] << 0)  | 
                       (key[i*4 + 1] << 8)  | 
                       (key[i*4 + 2] << 16) | 
                       (key[i*4 + 3] << 24);
    }

    // Block counter
    state[12] = counter;

    // Load nonce
    for (int i = 0; i < 3; i++) {
        state[13 + i] = (nonce[i*4 + 0] << 0)  | 
                        (nonce[i*4 + 1] << 8)  | 
                        (nonce[i*4 + 2] << 16) | 
                        (nonce[i*4 + 3] << 24);
    }

    uint8_t stream[64];
    size_t offset = 0;

    while (length > 0) {
        chacha20_block(state, stream);
        state[12]++; // Increment counter

        size_t bytes_to_crypt = (length < 64) ? length : 64;
        
        for (size_t i = 0; i < bytes_to_crypt; i++) {
            out[offset + i] = in[offset + i] ^ stream[i];
        }

        length -= bytes_to_crypt;
        offset += bytes_to_crypt;
    }
}
