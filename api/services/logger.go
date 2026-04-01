package services

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"

	"omnitools/core"
)

var (
	logMutex   sync.Mutex
	logFile    *os.File
	currentDay string
)

// Wilayah Suci, kebal dari Janitor
var LogDirectory = "logs"

// InitLogger dijalankan saat server pertama kali menyala (Fase Booting main.go)
func InitLogger() {
	pwd, _ := os.Getwd()
	LogDirectory = core.ResolveLogPath()
	fmt.Printf("📂 [DEBUG] PWD: %s | LogDirectory: %s\n", pwd, LogDirectory)
	// Pastikan folder logs eksis dari ketiadaan
	os.MkdirAll(LogDirectory, os.ModePerm)
	rotateLogFile()
	WriteLog("SYSTEM", "INFO", "Kotak Hitam OMNI TOOLS diaktifkan. Jaringan Sandboxing termonitor penuh.")
}

// rotateLogFile bertugas mengecek tanggal. Jika berganti hari di tengah malam, pangkas menjadi file baru.
func rotateLogFile() {
	now := time.Now()
	today := now.Format("2006-01-02") // Format Standar Tanggal Rilis OS: YYYY-MM-DD

	// Jika masih di hari yang sama, teruskan menyalurkan tinta log ke file yang ada
	if currentDay == today && logFile != nil {
		return
	}

	// Jika pergantian fajar tiba, segel/tutup catatannya
	if logFile != nil {
		logFile.Close()
	}

	// Forge/Buka file baru eksklusif untuk aktivitas hari ini
	logPath := filepath.Join(LogDirectory, fmt.Sprintf("omni_system_%s.log", today))
	file, err := os.OpenFile(logPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatalf("🚨 GAGAL MENGAKTIFKAN KOTAK HITAM OMNI: %v", err)
	}

	logFile = file
	currentDay = today

	// Arahkan output log standar (bawaan Golang) ke file OMNI ini juga
	log.SetOutput(logFile)
}

// WriteLog - Fungsi Mutlak pencatatan Telemetri lintas-ruang (C++, Python, TSX, Gateway)
func WriteLog(layer string, code string, message string) {
	// KUNCI MEMORI: Tangkal bahaya tabrakan saat 1.000 thread mengontak API ini secara paralel!
	logMutex.Lock()
	defer logMutex.Unlock()

	rotateLogFile() // Menjamin kepastian waktu file hari ini

	timestamp := time.Now().Format("15:04:05.000")

	// The Omni Log Architecture Array Map
	logEntry := fmt.Sprintf("[%s] | %-16s | %-16s | %s\n", timestamp, layer, code, message)

	// Pemahatan Fisik secara Permanen
	if logFile != nil {
		logFile.WriteString(logEntry)
	}

	// Replika Siaran ke Layar Terminal C-Level (memudahkan Kapten dalam Mode `omni dev`)
	fmt.Print(logEntry)

	// Broadcaster Lintas Ruang Angkasa (Monitor UI SSE)
	BroadcastLog(layer, code, message)
}
