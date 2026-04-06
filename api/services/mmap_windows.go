//go:build windows

package services

import (
	"fmt"
	"os"
	"syscall"
	"unsafe"
)

// ==========================================
// BUKA FILE DENGAN MMAP (Windows via CreateFileMapping)
// ==========================================
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

	data := unsafe.Slice((*byte)(unsafe.Pointer(ptr)), fileSize)

	file.Close()

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
