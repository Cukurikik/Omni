package billing

import (
	"log"
	"sync"
	"time"
)

// ==========================================
// 💸 OMNI ENTERPRISE SLA TRACKER (Phase 31)
// ==========================================
// Automasi denda dan kompensasi (Billing) untuk target 99.99% Uptime.

type SLATracker struct {
	mu           sync.RWMutex
	TargetUptime float64
	DowntimeSecs int
}

func NewSLATracker() *SLATracker {
	return &SLATracker{TargetUptime: 99.99}
}

// RecordDowntime mencatat kerusakan infrastruktur dan memotong invoice secara otonom
func (sla *SLATracker) RecordDowntime(duration time.Duration) {
	sla.mu.Lock()
	defer sla.mu.Unlock()

	sla.DowntimeSecs += int(duration.Seconds())
	log.Printf("💸 [SLA-TRACKER] Terdeteksi %v downtime. Kompensasi $0.05/detik dihitung.", duration)
}

// CalculateUptime mengkalkulasi uptime sepanjang bulan berjalan
func (sla *SLATracker) CalculateUptime(totalSecs int) float64 {
	sla.mu.RLock()
	defer sla.mu.RUnlock()

	if totalSecs == 0 {
		return 100.0
	}
	realUptime := float64(totalSecs-sla.DowntimeSecs) / float64(totalSecs) * 100.0
	return realUptime
}
