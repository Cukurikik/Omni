package engine

/*
// ==========================================
// ⚡ OMNI-KINETIC: CGO Bridge Configuration
// ==========================================
// Menginstruksikan Go Compiler untuk ikut mengompilasi kode C native
// dan mengoptimalkannya dengan flag -O3 (Maximum Speed Optimization)
#cgo CFLAGS: -O3 -Wall
#cgo windows LDFLAGS: -lkernel32

#include "kinetic_engine.h"
#include <stdlib.h>
*/
import "C"

import (
	"fmt"
	"log"
	"time"
	"unsafe"
)

// ==========================================
// ⚡ OMNI-KINETIC: Golang → C Bridge Functions
// ==========================================
// Setiap fungsi mengubah string Go menjadi pointer C,
// memanggil fungsi C bare-metal, lalu membebaskan memori.
//
// RAM terpakai di Go: hanya pointer + error handling
// RAM terpakai di C:  ~4MB buffer (Windows) atau mmap virtual (Linux)
// ==========================================

// KineticVersion mengembalikan versi engine C native
func KineticVersion() string {
	return C.GoString(C.kinetic_version())
}

// KineticXorEncrypt melakukan enkripsi/dekripsi XOR pada file menggunakan C engine
// File 50GB diproses tanpa memuat ke RAM!
//
// Contoh: KineticXorEncrypt("video.mp4", "video.enc", 0x5A)
// Untuk dekripsi: panggil dengan kunci yang sama (XOR bersifat reversible)
func KineticXorEncrypt(inputPath, outputPath string, xorKey byte) error {
	start := time.Now()

	log.Printf("⚡ [OMNI-KINETIC] XOR Encrypt dimulai | Key: 0x%02X | Input: %s", xorKey, inputPath)

	cInput := C.CString(inputPath)
	cOutput := C.CString(outputPath)
	defer C.free(unsafe.Pointer(cInput))
	defer C.free(unsafe.Pointer(cOutput))

	// 🚀 PANGGIL FUNGSI C SECARA LANGSUNG DARI MEMORI!
	result := C.kinetic_xor_encrypt(cInput, cOutput, C.uchar(xorKey))

	elapsed := time.Since(start)

	if result != 0 {
		errMsg := kineticErrorToString(int(result))
		log.Printf("❌ [OMNI-KINETIC] XOR Encrypt gagal: %s (kode: %d) [%v]", errMsg, int(result), elapsed)
		return fmt.Errorf("KINETIC_XOR_ENCRYPT_FAILED: %s (kode: %d)", errMsg, int(result))
	}

	log.Printf("✅ [OMNI-KINETIC] XOR Encrypt selesai dalam %v | Output: %s", elapsed, outputPath)
	return nil
}

// KineticByteInvert menginversi setiap byte dalam file (~byte)
// Berguna untuk efek negatif foto, scrambling data, dll.
func KineticByteInvert(inputPath, outputPath string) error {
	start := time.Now()

	log.Printf("⚡ [OMNI-KINETIC] Byte Invert dimulai | Input: %s", inputPath)

	cInput := C.CString(inputPath)
	cOutput := C.CString(outputPath)
	defer C.free(unsafe.Pointer(cInput))
	defer C.free(unsafe.Pointer(cOutput))

	result := C.kinetic_byte_invert(cInput, cOutput)

	elapsed := time.Since(start)

	if result != 0 {
		errMsg := kineticErrorToString(int(result))
		log.Printf("❌ [OMNI-KINETIC] Byte Invert gagal: %s (kode: %d) [%v]", errMsg, int(result), elapsed)
		return fmt.Errorf("KINETIC_BYTE_INVERT_FAILED: %s (kode: %d)", errMsg, int(result))
	}

	log.Printf("✅ [OMNI-KINETIC] Byte Invert selesai dalam %v | Output: %s", elapsed, outputPath)
	return nil
}

// KineticChecksum menghitung checksum XOR dari seluruh file
// Ultra-cepat: O(n) time, O(1) memory — bahkan untuk file 50GB
func KineticChecksum(filePath string) (uint32, error) {
	start := time.Now()

	cPath := C.CString(filePath)
	defer C.free(unsafe.Pointer(cPath))

	var checksum C.uint

	result := C.kinetic_checksum(cPath, &checksum)

	elapsed := time.Since(start)

	if result != 0 {
		errMsg := kineticErrorToString(int(result))
		return 0, fmt.Errorf("KINETIC_CHECKSUM_FAILED: %s (kode: %d)", errMsg, int(result))
	}

	log.Printf("⚡ [OMNI-KINETIC] Checksum: 0x%08X [%v] | File: %s", uint32(checksum), elapsed, filePath)
	return uint32(checksum), nil
}

// kineticErrorToString mengonversi kode error C ke pesan yang bisa dibaca manusia
func kineticErrorToString(code int) string {
	switch code {
	case -1:
		return "Gagal membuka file input (KINETIC_ERR_OPEN_IN)"
	case -2:
		return "Gagal membuka/membuat file output (KINETIC_ERR_OPEN_OUT)"
	case -3:
		return "Gagal melakukan Memory Mapping (KINETIC_ERR_MAP_FAILED)"
	case -4:
		return "Gagal mengalokasikan memori (KINETIC_ERR_ALLOC)"
	case -5:
		return "Gagal menulis ke file output (KINETIC_ERR_WRITE)"
	case -6:
		return "Gagal membaca file input (KINETIC_ERR_READ)"
	default:
		return fmt.Sprintf("Error tidak dikenal (kode: %d)", code)
	}
}
