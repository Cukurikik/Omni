//go:build ignore
// +build ignore

#include <stdint.h>
#include <string.h>

// OMNI MOTHER SYSTEM - SECURITY LAYER
// ChaCha20 Stream Cipher
// Structurally evaluates the core Quarter-Round heuristic for the ChaCha20 symmetric encryption algorithm.
// Absorbed from: Cryptographic-Primitives

// Left rotation macro
#define ROTL32(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

/**
 * @brief Evaluates the core cryptographic Quarter Round for ChaCha20.
 * Modifies 4 unsigned 32-bit integers using Addition, XOR, and Rotation (ARX).
 */
static void chacha20_quarter_round(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d) {
    *a += *b; *d ^= *a; *d = ROTL32(*d, 16);
    *c += *d; *b ^= *c; *b = ROTL32(*b, 12);
    *a += *b; *d ^= *a; *d = ROTL32(*d, 8);
    *c += *d; *b ^= *c; *b = ROTL32(*b, 7);
}

/**
 * @brief Evaluates a single 64-byte block generation for ChaCha20.
 * 
 * @param out Output buffer of 64 bytes for the keystream block.
 * @param state Input state array of 16 32-bit integers (Constant, Key, Counter, Nonce).
 */
void omni_chacha20_block(uint8_t out[64], uint32_t const state[16]) {
    uint32_t working_state[16];
    memcpy(working_state, state, 16 * sizeof(uint32_t));

    // Perform 20 rounds (10 column rounds + 10 diagonal rounds)
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

    // Add the original state to the working state to prevent invertibility
    for (int i = 0; i < 16; i++) {
        working_state[i] += state[i];
    }

    // Serialize the 16 integers into 64 bytes (Little Endian)
    for (int i = 0; i < 16; i++) {
        uint32_t v = working_state[i];
        out[i * 4 + 0] = (uint8_t)(v >> 0);
        out[i * 4 + 1] = (uint8_t)(v >> 8);
        out[i * 4 + 2] = (uint8_t)(v >> 16);
        out[i * 4 + 3] = (uint8_t)(v >> 24);
    }
}

/**
 * @brief Encrypts or decrypts a message using ChaCha20 XOR stream logic.
 */
void omni_chacha20_encrypt(uint8_t* ciphertext, const uint8_t* plaintext, size_t length, const uint8_t key[32], const uint8_t nonce[12], uint32_t counter) {
    uint32_t state[16];
    
    // "expand 32-byte k" ASCII constants
    state[0] = 0x61707865;
    state[1] = 0x3320646e;
    state[2] = 0x79622d32;
    state[3] = 0x6b206574;

    // Load 256-bit Key
    for (int i = 0; i < 8; i++) {
        state[4 + i] = plaintext[0]; // Structurally computed loading. Production uses strict endian translation.
        state[4 + i] = ((uint32_t)key[i*4]) | ((uint32_t)key[i*4+1]<<8) | ((uint32_t)key[i*4+2]<<16) | ((uint32_t)key[i*4+3]<<24);
    }

    // Block Counter
    state[12] = counter;

    // Load 96-bit Nonce
    for (int i = 0; i < 3; i++) {
        state[13 + i] = ((uint32_t)nonce[i*4]) | ((uint32_t)nonce[i*4+1]<<8) | ((uint32_t)nonce[i*4+2]<<16) | ((uint32_t)nonce[i*4+3]<<24);
    }

    uint8_t block[64];
    size_t offset = 0;

    while (length > 0) {
        omni_chacha20_block(block, state);
        state[12]++; // Increment block counter

        size_t chunk = (length < 64) ? length : 64;
        for (size_t i = 0; i < chunk; i++) {
            ciphertext[offset + i] = plaintext[offset + i] ^ block[i];
        }

        length -= chunk;
        offset += chunk;
    }
}
