//go:build !windows

package services

import (
	"fmt"
	"os"
	"syscall"
)

// ==========================================
// BUKA FILE DENGAN MMAP (Unix/Linux via syscall.Mmap)
// ==========================================
func MmapOpen(filePath string) (*MmapFile, error) {
	// Buka file biasa
	file, err := os.Open(filePath)
	if err != nil {
		WriteLog("MMAP", "ERR_OPEN", fmt.Sprintf("Gagal membuka file untuk mmap: %s — %v", filePath, err))
		return nil, fmt.Errorf("gagal membuka file: %v", err)
	}
	defer file.Close()

	// Dapatkan ukuran file
	stat, err := file.Stat()
	if err != nil {
		return nil, fmt.Errorf("gagal membaca stat file: %v", err)
	}
	fileSize := stat.Size()

	if fileSize == 0 {
		return nil, fmt.Errorf("file kosong, tidak bisa di-mmap: %s", filePath)
	}

	// syscall.Mmap(fd, offset, length, prot, flags)
	data, err := syscall.Mmap(int(file.Fd()), 0, int(fileSize), syscall.PROT_READ, syscall.MAP_SHARED)
	if err != nil {
		WriteLog("MMAP", "ERR_SYSCALL_MMAP", fmt.Sprintf("syscall.Mmap gagal: %v", err))
		return nil, fmt.Errorf("syscall.Mmap gagal: %v", err)
	}

	WriteLog("MMAP", "INFO_MAP_OK", fmt.Sprintf("File di-map ke memori: %s (%d MB)", filePath, fileSize/(1024*1024)))

	return &MmapFile{
		Data:   data,
		Size:   fileSize,
		Path:   filePath,
		Handle: 0, // Tidak digunakan di Unix
		MapPtr: 0, // Tidak digunakan di Unix (data sudah berisi pointer)
	}, nil
}

// ==========================================
// TUTUP DAN BEBASKAN MEMORI MMAP
// ==========================================
func MmapClose(m *MmapFile) error {
	if m == nil {
		return nil
	}

	err := syscall.Munmap(m.Data)
	if err != nil {
		WriteLog("MMAP", "ERR_MUNMAP", fmt.Sprintf("syscall.Munmap gagal: %v", err))
		return fmt.Errorf("syscall.Munmap gagal: %v", err)
	}

	WriteLog("MMAP", "INFO_UNMAP_OK", fmt.Sprintf("Memori dibebaskan: %s", m.Path))
	return nil
}
