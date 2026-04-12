package gc_tuner

import (
	"log"
	"runtime/debug"
	"time"
)

// ==========================================
// 🧹 OMNI GC TUNER (Phase 34)
// ==========================================
// Mencegah spike CPU yang diakibatkan oleh Garbage Collection di Go.
// Melakukan throttle GC secara native ke 900% (Manual Triggering).

func IgniteGCPacer() {
	// Set memori GC target 900% dari baseline untuk mengurangi frekuensi STW (Stop The World)
	previousPercent := debug.SetGCPercent(900)
	log.Printf("🧹 [GC-TUNER] OMNI Memicu GC Override: %d%% -> 900%%", previousPercent)

	go func() {
		// Cron Job Native: Membersihkan sisa memori saat CPU idle
		ticker := time.NewTicker(30 * time.Minute)
		defer ticker.Stop()

		for range ticker.C {
			log.Println("🧹 [GC-TUNER] Memaksakan Pembersihan Memori Manual (OOM Override)...")
			debug.FreeOSMemory()
		}
	}()
}
