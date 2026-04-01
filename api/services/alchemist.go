package services

import (
	"crypto/rand"
	"fmt"
	"os"
	"path/filepath"
)

// ==========================================
// THE ALCHEMIST (Zero-Downtime Hot-Swapping)
// ==========================================
// Memanipulasi file binari eksekusi C++/Python saat mesin sedang beroperasi penuh.
// Menggunakan teknik Inode Symlink POSIX.

const EngineDir = "../release/engines"

// InitAlchemist memastikan markas bawah tanah "Engines" siap
func InitAlchemist() {
	if _, err := os.Stat(EngineDir); os.IsNotExist(err) {
		os.MkdirAll(EngineDir, os.ModePerm)
	}
	WriteLog("ALCHEMIST", "INFO_INIT", "Lab Alchemist (Engine Bunker) Siaga.")
}

// ResolveBinary mencari apakah Master Admin sudah men-deploy mesin custom
// ke dalam bunker dengan nama "binary_current".
// Jika tidak ada, fungsi akan mengandalkan PATH bawaan dari Server OS Kernel.
func ResolveBinary(binaryName string) string {
	// 1. Mencoba melacak mesin rahasia OMNI terlebih dahulu
	targetCurrentLink := filepath.Join(EngineDir, fmt.Sprintf("%s_current", binaryName))

	// Jika symlink "ffmpeg_current" ada, kita pakai biner custom yang ada di Bunker ini.
	if _, err := os.Stat(targetCurrentLink); err == nil {
		WriteLog("ALCHEMIST", "INFO_RESOLVED", fmt.Sprintf("Proxy Biner dialihkan ke Bunker: %s", targetCurrentLink))
		return targetCurrentLink
	}

	// 2. Jika tidak ada di Bunker, biarkan OS mencari di /usr/bin atau System PATH
	return binaryName
}

// SwapBinaryEngine melakukan Atom Swap ke Biner baru yang di-upload.
// Semua Worker (Video/Audio) akan tiba-tiba mengeksekusi Biner versi terbaru
// tanpa mengalami satupun CRASH pada task yang sedang live (Zero-Downtime).
func SwapBinaryEngine(binaryName string, newAbsPath string) error {
	targetCurrentLink := filepath.Join(EngineDir, fmt.Sprintf("%s_current", binaryName))

	// Untuk melakukan Atomic Swap Posix, kita tidak boleh menimpa file secara mentah.
	// Jika kita HAPUS symlink lama lalu BUAT symlink baru, ada celah 1 milidetik di mana
	// executor CLI akan GAGAL mencari binary, dan me-return HTTP 500.

	// 💥 CARA ATOMIC (Zero-Downtime Murni): Bikin Symlink Sementara, dan Lakukan RENAME!
	// Rename Symlink akan memaksa Kernel me-replace File Table tanpa celah sekecil apapun.
	b := make([]byte, 4)
	rand.Read(b)
	tempLink := filepath.Join(EngineDir, fmt.Sprintf("%s_temp_%x", binaryName, b))

	// 1. Buat benang takdir (symlink) sementara yang mengikat ke biner mesin terbaru
	err := os.Symlink(newAbsPath, tempLink)
	if err != nil {
		WriteLog("ALCHEMIST", "ERR_SYMLINK", fmt.Sprintf("Gagal menyuntik Inode: %v", err))
		return err
	}

	// 2. ATOMIC RENAME (Menyilangkan benang secara instan menimpa `_current`)
	err = os.Rename(tempLink, targetCurrentLink)
	if err != nil {
		os.Remove(tempLink) // Sapu bersih jika gagal
		WriteLog("ALCHEMIST", "ERR_ATOMIC_RENAME", fmt.Sprintf("Gagal Swap Mesin Atomic: %v", err))
		return err
	}

	WriteLog("ALCHEMIST", "INFO_HOT_SWAP", fmt.Sprintf("ZERO_DOWNTIME_SWAP Sukses mutlak: [%s] -> %s", binaryName, newAbsPath))
	return nil
}
