package core

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

const (
	MaxLogFileSize   = 50 * 1024 * 1024 // 50MB
	LogCheckInterval = 1 * time.Hour
)

// StartBlackbox memulai daemon background yang merotasi log agar tidak membengkak.
// Disebut juga The Omni Janitor for Logs.
func StartBlackbox() {
	log.Println("⬛ [OMNI-BLACKBOX] Daemon Pencatat Kotak Hitam diaktifkan. Memonitor log > 50MB...")

	var logDir string
	if AppConfig != nil && AppConfig.Storage.QuarantineDir != "" {
		// Asumsi rilis log di folder 'logs' yang selevel dengan quarantine_dir
		logDir = filepath.Join(filepath.Dir(AppConfig.Storage.QuarantineDir), "logs")
	} else {
		logDir = "../release/logs"
	}

	_ = os.MkdirAll(logDir, 0755)

	outLogPath := filepath.Join(logDir, "omni-out.log")
	errLogPath := filepath.Join(logDir, "omni-err.log")

	// Pemanasan: cek saat pertama nyala
	rotateIfExceeds(outLogPath)
	rotateIfExceeds(errLogPath)

	ticker := time.NewTicker(LogCheckInterval)
	defer ticker.Stop()

	for range ticker.C {
		rotateIfExceeds(outLogPath)
		rotateIfExceeds(errLogPath)
	}
}

// rotateIfExceeds melakukan rotasi log apabila sudah melebihi batas MaxLogFileSize
func rotateIfExceeds(filePath string) {
	info, err := os.Stat(filePath)
	if os.IsNotExist(err) {
		return
	}
	if err != nil {
		log.Printf("⚠️ [OMNI-BLACKBOX] Gagal memeriksa %s: %v", filePath, err)
		return
	}

	if info.Size() >= MaxLogFileSize {
		timestamp := time.Now().Format("2006-01-02_15-04-05")
		rotatedPath := fmt.Sprintf("%s.%s.bak", filePath, timestamp)

		log.Printf("⬛ [OMNI-BLACKBOX] Merotasi Log Terlalu Besar: %s -> %s", filePath, rotatedPath)

		err := os.Rename(filePath, rotatedPath)
		if err != nil {
			log.Printf("❌ [OMNI-BLACKBOX] Gagal merotasi log: %v", err)
			return
		}

		// Buat file baru kosong untuk menjaga konsistensi jika ada appender lain
		file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
		if err == nil {
			file.Close()
		}
	}
}
