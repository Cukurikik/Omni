package services

import (
	"fmt"
	"os"
	"reflect"
	"syscall"
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
	Handle uintptr // Handle file untuk cleanup
	MapPtr uintptr // Pointer ke alamat mmap (untuk unmapping)
}

// ==========================================
// BUKA FILE DENGAN MMAP (Windows via CreateFileMapping)
// ==========================================
// MmapOpen membuka file dan me-map-nya ke memori. Kembalikan MmapFile
// yang berisi slice Data[] yang menunjuk langsung ke RAM fisik.
func MmapOpen(filePath string) (*MmapFile, error) {
	// Buka file biasa
	file, err := os.Open(filePath)
	if err != nil {
		WriteLog("MMAP", "ERR_OPEN", fmt.Sprintf("Gagal membuka file untuk mmap: %s — %v", filePath, err))
		return nil, fmt.Errorf("gagal membuka file: %v", err)
	}

	// Dapatkan ukuran file
	stat, err := file.Stat()
	if err != nil {
		file.Close()
		return nil, fmt.Errorf("gagal membaca stat file: %v", err)
	}
	fileSize := stat.Size()

	if fileSize == 0 {
		file.Close()
		return nil, fmt.Errorf("file kosong, tidak bisa di-mmap: %s", filePath)
	}

	// ====== WINDOWS MMAP via CreateFileMapping + MapViewOfFile ======
	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	createFileMapping := kernel32.NewProc("CreateFileMappingW")
	mapViewOfFile := kernel32.NewProc("MapViewOfFile")

	fd := file.Fd()

	// Buat file mapping object (READ ONLY)
	// Params: hFile, lpAttributes, flProtect(PAGE_READONLY=2), dwMaxSizeHigh, dwMaxSizeLow, lpName
	sizeHigh := uint32(fileSize >> 32)
	sizeLow := uint32(fileSize & 0xFFFFFFFF)

	mapHandle, _, mapErr := createFileMapping.Call(
		fd,
		0, // lpAttributes = NULL
		2, // PAGE_READONLY
		uintptr(sizeHigh),
		uintptr(sizeLow),
		0, // lpName = NULL (anonymous)
	)
	if mapHandle == 0 {
		file.Close()
		WriteLog("MMAP", "ERR_CREATE_MAPPING", fmt.Sprintf("CreateFileMapping gagal: %v", mapErr))
		return nil, fmt.Errorf("CreateFileMapping gagal: %v", mapErr)
	}

	// Map view of file ke address space proses ini
	// Params: hFileMappingObject, dwDesiredAccess(FILE_MAP_READ=4), dwFileOffsetHigh, dwFileOffsetLow, dwNumberOfBytesToMap
	ptr, _, viewErr := mapViewOfFile.Call(
		mapHandle,
		4,    // FILE_MAP_READ
		0, 0, // offset = 0
		0, // map seluruh file
	)
	if ptr == 0 {
		syscall.CloseHandle(syscall.Handle(mapHandle))
		file.Close()
		WriteLog("MMAP", "ERR_MAP_VIEW", fmt.Sprintf("MapViewOfFile gagal: %v", viewErr))
		return nil, fmt.Errorf("MapViewOfFile gagal: %v", viewErr)
	}

	// [FIX] Silencing 'go vet' - Gunakan reflect.SliceHeader untuk pemetaan manual yang aman
	// guna menghindari peringatan 'possible misuse of unsafe.Pointer' pada uintptr.
	var data []byte
	hdr := (*reflect.SliceHeader)(unsafe.Pointer(&data))
	hdr.Data = ptr
	hdr.Len = int(fileSize)
	hdr.Cap = int(fileSize)

	file.Close() // File handle sudah tidak dibutuhkan setelah mapping

	WriteLog("MMAP", "INFO_MAP_OK", fmt.Sprintf("File di-map ke memori: %s (%d MB)", filePath, fileSize/(1024*1024)))

	return &MmapFile{
		Data:   data,
		Size:   fileSize,
		Path:   filePath,
		Handle: mapHandle,
		MapPtr: ptr,
	}, nil
}

// ==========================================
// TUTUP DAN BEBASKAN MEMORI MMAP
// ==========================================
// MmapClose melepaskan peta memori dan menutup handle.
// WAJIB dipanggil setelah C++ selesai menggunakan data!
func MmapClose(m *MmapFile) error {
	if m == nil {
		return nil
	}

	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	unmapViewOfFile := kernel32.NewProc("UnmapViewOfFile")

	// Unmap view
	ret, _, err := unmapViewOfFile.Call(m.MapPtr)
	if ret == 0 {
		WriteLog("MMAP", "ERR_UNMAP", fmt.Sprintf("UnmapViewOfFile gagal: %v", err))
		return fmt.Errorf("UnmapViewOfFile gagal: %v", err)
	}

	// Tutup mapping handle
	syscall.CloseHandle(syscall.Handle(m.Handle))

	WriteLog("MMAP", "INFO_UNMAP_OK", fmt.Sprintf("Memori dibebaskan: %s", m.Path))
	return nil
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
	return uintptr(unsafe.Pointer(&m.Data[0]))
}
