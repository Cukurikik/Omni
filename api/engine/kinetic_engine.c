// ==========================================
// ⚡ OMNI-KINETIC: Native C Engine Implementation
// ==========================================
// Bare-metal file processing: XOR encrypt, byte invert, checksum.
// Dioptimalkan untuk streaming — file berukuran besar diproses tanpa
// memuat seluruhnya ke RAM.
// ==========================================

#include "kinetic_engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KINETIC_VERSION "1.0.0-SOVEREIGN"
#define KINETIC_BUFFER_SIZE (4 * 1024 * 1024) // 4MB buffer

// Error codes
#define KINETIC_OK           0
#define KINETIC_ERR_OPEN_IN -1
#define KINETIC_ERR_OPEN_OUT -2
#define KINETIC_ERR_MAP     -3
#define KINETIC_ERR_ALLOC   -4
#define KINETIC_ERR_WRITE   -5
#define KINETIC_ERR_READ    -6

const char* kinetic_version(void) {
    return KINETIC_VERSION;
}

int kinetic_xor_encrypt(const char* input_path, const char* output_path, unsigned char xor_key) {
    FILE* fin = fopen(input_path, "rb");
    if (!fin) return KINETIC_ERR_OPEN_IN;

    FILE* fout = fopen(output_path, "wb");
    if (!fout) { fclose(fin); return KINETIC_ERR_OPEN_OUT; }

    unsigned char* buffer = (unsigned char*)malloc(KINETIC_BUFFER_SIZE);
    if (!buffer) { fclose(fin); fclose(fout); return KINETIC_ERR_ALLOC; }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, KINETIC_BUFFER_SIZE, fin)) > 0) {
        for (size_t i = 0; i < bytes_read; i++) {
            buffer[i] ^= xor_key;
        }
        size_t written = fwrite(buffer, 1, bytes_read, fout);
        if (written != bytes_read) {
            free(buffer); fclose(fin); fclose(fout);
            return KINETIC_ERR_WRITE;
        }
    }

    free(buffer);
    fclose(fin);
    fclose(fout);
    return KINETIC_OK;
}

int kinetic_byte_invert(const char* input_path, const char* output_path) {
    FILE* fin = fopen(input_path, "rb");
    if (!fin) return KINETIC_ERR_OPEN_IN;

    FILE* fout = fopen(output_path, "wb");
    if (!fout) { fclose(fin); return KINETIC_ERR_OPEN_OUT; }

    unsigned char* buffer = (unsigned char*)malloc(KINETIC_BUFFER_SIZE);
    if (!buffer) { fclose(fin); fclose(fout); return KINETIC_ERR_ALLOC; }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, KINETIC_BUFFER_SIZE, fin)) > 0) {
        for (size_t i = 0; i < bytes_read; i++) {
            buffer[i] = ~buffer[i];
        }
        size_t written = fwrite(buffer, 1, bytes_read, fout);
        if (written != bytes_read) {
            free(buffer); fclose(fin); fclose(fout);
            return KINETIC_ERR_WRITE;
        }
    }

    free(buffer);
    fclose(fin);
    fclose(fout);
    return KINETIC_OK;
}

int kinetic_checksum(const char* file_path, unsigned int* out_checksum) {
    FILE* fin = fopen(file_path, "rb");
    if (!fin) return KINETIC_ERR_OPEN_IN;

    unsigned char* buffer = (unsigned char*)malloc(KINETIC_BUFFER_SIZE);
    if (!buffer) { fclose(fin); return KINETIC_ERR_ALLOC; }

    unsigned int checksum = 0;
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, KINETIC_BUFFER_SIZE, fin)) > 0) {
        for (size_t i = 0; i < bytes_read; i++) {
            checksum ^= ((unsigned int)buffer[i]) << ((i % 4) * 8);
        }
    }

    *out_checksum = checksum;
    free(buffer);
    fclose(fin);
    return KINETIC_OK;
}
