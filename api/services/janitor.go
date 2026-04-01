package services

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

// Konfigurasi Aturan Pemusnahan Ephemeral
const (
	CacheTTL      = 1 * time.Hour   // Umur maksimal file (1 Jam)
	SweepInterval = 5 * time.Minute // Interval patroli janitor
)

// Daftar folder yang diawasi oleh Janitor
var TargetDirectories = []string{
	"../release/omni_quarantine", // Tempat isolasi / karantina mentah
	"../release/omni_cache",      // Tempat cache render sementara
}

// StartCacheDestroyer adalah fungsi yang berjalan abadi di latar belakang
func StartCacheDestroyer() {
	ticker := time.NewTicker(SweepInterval)
	defer ticker.Stop()

	log.Println("🧹 [OMNI JANITOR] Sistem Pemusnahan Ephemeral diaktifkan. Berpatroli setiap 5 menit.")

	for range ticker.C {
		runSweepCycle()
	}
}

// Logika penyisiran dan pemusnahan dengan Telemetry (Laporan Ukuran Memori)
func runSweepCycle() {
	now := time.Now()
	deletedCount := 0
	freedSpace := int64(0)

	for _, dir := range TargetDirectories {
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			continue
		}

		filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil // Abaikan file yang sedang dikunci/sulit diakses
			}

			if !info.IsDir() {
				fileAge := now.Sub(info.ModTime())

				// 1. CEK FILE TUS BESI PORTABLE (TTL 24 JAM)
				// Jika file diakhiri ".info" (TUS Metadata) atau merupakan base TUS (tanpa ektensi)
				isTusFile := false
				if filepath.Ext(path) == ".info" || filepath.Ext(path) == "" {
					isTusFile = true
				}

				// Vonis Kematian OMNI TOOLS
				willDelete := false
				if isTusFile && fileAge > 24*time.Hour { // File TUS hangus jika > 1 hari internet putus total
					willDelete = true
				} else if !isTusFile && fileAge > CacheTTL { // File biasa hangus > 1 Jam
					willDelete = true
				}

				if willDelete {
					fileSize := info.Size()
					errDel := os.Remove(path)
					if errDel == nil {
						deletedCount++
						freedSpace += fileSize
					}
				}
			}
			return nil
		})
	}

	// Cetak log (Telemetry) hanya jika ada pemusnahan sukses, agar log terminal tidak berisik
	if deletedCount > 0 {
		freedMB := float64(freedSpace) / (1024 * 1024)
		fmt.Printf("🔥 [OMNI JANITOR] Pemusnahan Selesai: %d file kadaluarsa dihapus. Menghemat %.2f MB storage.\n", deletedCount, freedMB)
	}
}
