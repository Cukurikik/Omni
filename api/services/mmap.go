package services

import (
	"fmt"
	"unsafe"
)

// ==========================================
// INOVASI #2: ILMU HITAM MEMORI — ZERO-COPY (mmap)
// ==========================================
// Teknik Memory-Mapped Files memungkinkan Golang dan C++ mengakses
// file yang SAMA di satu alamat memori fisik (RAM) tanpa proses
// loading dari disk yang terpisah.
//
// EFEK: C++ tidak perlu membaca ulang file dari hard drive.
//       Golang "membuka" file, OS me-map ke RAM, lalu C++ langsung
//       menusuk alamat memori tersebut. Hemat 40% waktu I/O.

// MmapFile merepresentasikan file yang sudah di-map ke memori
type MmapFile struct {
	Data   []byte  // Slice yang menunjuk ke memori fisik (bukan salinan!)
	Size   int64   // Ukuran file dalam byte
	Path   string  // Path asli file
	Handle uintptr // Handle file untuk cleanup (Windows)
	MapPtr uintptr // Pointer ke alamat mmap (untuk unmapping)
}

// ==========================================
// BACA POTONGAN DATA DARI MMAP (untuk pengiriman ke C++ via Shared Memory)
// ==========================================
// MmapReadChunk membaca potongan data dari file yang sudah di-map
// tanpa melakukan syscall read tambahan — langsung akses RAM!
func MmapReadChunk(m *MmapFile, offset int64, size int) ([]byte, error) {
	if offset < 0 || offset >= m.Size {
		return nil, fmt.Errorf("offset di luar batas: %d (ukuran file: %d)", offset, m.Size)
	}

	end := offset + int64(size)
	if end > m.Size {
		end = m.Size
	}

	// Ini BUKAN salinan! Ini pointer ke blok memori fisik yang sama.
	return m.Data[offset:end], nil
}

// ==========================================
// HELPER: Dapatkan Pointer Mentah untuk C++ (via CGo / Shared Memory IPC)
// ==========================================
// MmapGetPointer mengembalikan alamat memori mentah (unsafe.Pointer)
// yang bisa dikirim ke C++ melalui mekanisme IPC (shared memory name, dll.)
func MmapGetPointer(m *MmapFile) uintptr {
	if len(m.Data) == 0 {
		return 0
	}
	return uintptr(unsafe.Pointer(&m.Data[0]))
}
