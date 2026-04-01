package core

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"runtime"
	"time"
)

// ==========================================
// 🪖 OMNI-NEXUS: WORKER TELEMETRY ENGINE
// ==========================================
// Jika server dinyalakan sebagai "worker", goroutine ini
// akan terus-menerus mengirimkan sinyal detak jantung
// ke Master Node setiap N detik.
//
// Payload: IP, ActiveJobs, MaxJobs, CPU%, RAM, Uptime
// ==========================================

var workerStartTime = time.Now()

// StartWorkerHeartbeat memulai transmisi detak jantung ke Master.
// myAddr: alamat IP:Port mesin ini yang bisa dijangkau Master.
func StartWorkerHeartbeat(myAddr string) {
	masterURL := AppConfig.NexusCluster.MasterURL
	interval := time.Duration(AppConfig.NexusCluster.HeartbeatIntervalSec) * time.Second
	if interval <= 0 {
		interval = 5 * time.Second
	}

	// Tentukan nama node dari hostname
	nodeName, err := os.Hostname()
	if err != nil {
		nodeName = "unknown-worker"
	}

	log.Printf("🪖 [NEXUS WORKER] Identitas: %s (%s)", myAddr, nodeName)
	log.Printf("🪖 [NEXUS WORKER] Memulai transmisi detak jantung ke %s", masterURL)
	log.Printf("🪖 [NEXUS WORKER] Interval: %s | Max Jobs: %d", interval, AppConfig.NexusCluster.WorkerMaxJobs)

	go func() {
		consecutiveFailures := 0
		maxBackoff := 30 * time.Second

		for {
			// Kumpulkan telemetri sistem
			var memStats runtime.MemStats
			runtime.ReadMemStats(&memStats)

			nodeInfo := WorkerNode{
				IPAddress:  myAddr,
				NodeName:   nodeName,
				ActiveJobs: GetCurrentActiveJobs(),
				MaxJobs:    AppConfig.NexusCluster.WorkerMaxJobs,
				CPUPercent: float64(runtime.NumGoroutine()), // Goroutine count sebagai proxy CPU load
				MemUsedMB:  int64(memStats.Alloc / 1024 / 1024),
				MemTotalMB: int64(memStats.Sys / 1024 / 1024),
				UptimeSec:  int64(time.Since(workerStartTime).Seconds()),
				Version:    AppConfig.Version,
			}

			payload, _ := json.Marshal(nodeInfo)
			req, err := http.NewRequest("POST", masterURL+"/api/nexus/heartbeat", bytes.NewBuffer(payload))
			if err != nil {
				log.Printf("⚠️ [NEXUS WORKER] Gagal membuat request: %v", err)
				time.Sleep(interval)
				continue
			}

			req.Header.Set("X-NEXUS-KEY", AppConfig.NexusCluster.ClusterSecret)
			req.Header.Set("Content-Type", "application/json")

			client := &http.Client{Timeout: 3 * time.Second}
			resp, err := client.Do(req)

			if err != nil {
				consecutiveFailures++
				backoff := interval * time.Duration(consecutiveFailures)
				if backoff > maxBackoff {
					backoff = maxBackoff
				}

				if consecutiveFailures == 1 {
					log.Printf("⚠️ [NEXUS WORKER] Koneksi ke Master terputus! Mencoba lagi dalam %s...", backoff)
				} else if consecutiveFailures%5 == 0 {
					log.Printf("⚠️ [NEXUS WORKER] Masih tidak bisa menghubungi Master (%d kali gagal). Backoff: %s",
						consecutiveFailures, backoff)
				}

				time.Sleep(backoff)
				continue
			}

			resp.Body.Close()

			// Koneksi berhasil
			if consecutiveFailures > 0 {
				log.Printf("✅ [NEXUS WORKER] Koneksi ke Master dipulihkan setelah %d kali gagal!", consecutiveFailures)
				consecutiveFailures = 0
			}

			time.Sleep(interval)
		}
	}()
}

// DetectMyAddress mendeteksi IP address dan port dari mesin ini.
// Untuk produksi, gunakan environment variable OMNI_NEXUS_ADDR.
// Fallback: host:port dari AppConfig.
func DetectMyAddress() string {
	// Prioritas 1: Environment Variable
	addr := os.Getenv("OMNI_NEXUS_ADDR")
	if addr != "" {
		return addr
	}

	// Prioritas 2: AppConfig server address
	return GetServerAddr()
}
