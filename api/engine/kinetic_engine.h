/*
 * ==========================================
 * ⚡ OMNI-KINETIC: Native C Hyper-Engine
 * ==========================================
 * Jembatan komunikasi antara Golang (CGO) dan mesin C/C++
 *
 * File ini menggunakan extern "C" agar dapat dipanggil
 * oleh CGO tanpa name mangling C++.
 * ==========================================
 */

#ifndef KINETIC_ENGINE_H
#define KINETIC_ENGINE_H

#ifdef __cplusplus
extern "C" {
#endif

/* Kode Error KINETIC */
#define KINETIC_OK               0
#define KINETIC_ERR_OPEN_IN     -1
#define KINETIC_ERR_OPEN_OUT    -2
#define KINETIC_ERR_MAP_FAILED  -3
#define KINETIC_ERR_ALLOC       -4
#define KINETIC_ERR_WRITE       -5
#define KINETIC_ERR_READ        -6

/*
 * kinetic_xor_encrypt — Enkripsi/Dekripsi XOR bit-level
 * Memproses file menggunakan Memory Mapping (Windows: CreateFileMapping,
 * Linux: mmap). RAM terpakai hanya ~buffer_size bytes!
 *
 * @param input_path   Path file input
 * @param output_path  Path file output
 * @param xor_key      Kunci XOR (0x00-0xFF)
 * @return 0 = sukses, negatif = error code
 */
int kinetic_xor_encrypt(const char* input_path, const char* output_path, unsigned char xor_key);

/*
 * kinetic_byte_invert — Inversi setiap byte (~byte)
 * Efek: Warna foto menjadi negatif, audio menjadi noise
 *
 * @param input_path   Path file input
 * @param output_path  Path file output
 * @return 0 = sukses, negatif = error code
 */
int kinetic_byte_invert(const char* input_path, const char* output_path);

/*
 * kinetic_checksum — Hitung checksum XOR dari seluruh file
 * Ultra-cepat: 1 pass, O(n) time, O(1) memory
 *
 * @param file_path    Path file
 * @param out_checksum Pointer ke output checksum
 * @return 0 = sukses, negatif = error code
 */
int kinetic_checksum(const char* file_path, unsigned int* out_checksum);

/*
 * kinetic_version — Mengembalikan versi engine
 */
const char* kinetic_version(void);

#ifdef __cplusplus
}
#endif

#endif /* KINETIC_ENGINE_H */
