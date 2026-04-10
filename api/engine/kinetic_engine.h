// ==========================================
// ⚡ OMNI-KINETIC: Native C Engine Header
// ==========================================
// Deklarasi fungsi C yang dipanggil oleh kinetic_bridge.go via CGO.
// Implementasi ada di kinetic_engine.c (atau akan di-link dari .lib/.dll)
// ==========================================

#ifndef KINETIC_ENGINE_H
#define KINETIC_ENGINE_H

#include <stddef.h>

// Mengembalikan versi engine sebagai string C
const char* kinetic_version(void);

// XOR encrypt/decrypt file secara streaming (O(1) memory)
// Returns: 0 = sukses, negative = error code
int kinetic_xor_encrypt(const char* input_path, const char* output_path, unsigned char xor_key);

// Inversi setiap byte dalam file (~byte operation)
// Returns: 0 = sukses, negative = error code
int kinetic_byte_invert(const char* input_path, const char* output_path);

// Hitung XOR checksum dari seluruh file
// Returns: 0 = sukses, negative = error code
int kinetic_checksum(const char* file_path, unsigned int* out_checksum);

#endif // KINETIC_ENGINE_H
