package net

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"
	"time"
)

// ==========================================
// 💾 OMNI-AURA: IMMORTAL QUEUE ENGINE (WAL)
// ==========================================
// Pemusnahan Redis & RabbitMQ dalam satu modul.
//
// ARSITEKTUR:
//   Write-Ahead Logging (WAL) — teknik yang sama digunakan PostgreSQL & SQLite.
//   Setiap job di-tulis ke SSD SEBELUM diproses, sehingga:
//   - Jika server mati listrik → job tetap di SSD → dilanjutkan saat boot
//   - Jika proses crash → WAL dibaca ulang → zero data loss
//
// KEUNGGULAN vs Redis:
//   Redis: Server terpisah, RAM-only (data hilang saat restart tanpa RDB/AOF)
//   AURA:  Built-in, SSD-persisted, zero-config, crash-proof
//
// ALUR:
//   1. Developer: dispatchBackgroundJob({name: "send_email", payload: {...}})
//   2. JS → OmniNative.syscall("queue_dispatch", ...) → Rust → Go
//   3. Go menulis job ke WAL file (SSD)
//   4. Worker Goroutine mengambil job dari WAL dan memprosesnya
//   5. Jika selesai → job dihapus dari WAL
//   6. Jika crash → WAL di-replay saat boot
// ==========================================

// AuraJob representasi satu tugas di dalam queue
type AuraJob struct {
	ID        string                 `json:"id"`
	Name      string                 `json:"name"`
	Payload   map[string]interface{} `json:"payload"`
	Status    string                 `json:"status"` // pending, processing, done, failed
	Retries   int                    `json:"retries"`
	MaxRetry  int                    `json:"max_retry"`
	CreatedAt int64                  `json:"created_at"`
	UpdatedAt int64                  `json:"updated_at"`
	Error     string                 `json:"error,omitempty"`
}

// AuraConfig konfigurasi queue engine
type AuraConfig struct {
	WALDir         string        // Direktori WAL files
	MaxWorkers     int           // Jumlah worker consumer
	RetryDelay     time.Duration // Delay antar retry
	MaxRetries     int           // Maks retry per job
	FlushInterval  time.Duration // Interval flush WAL ke disk
}

// DefaultAuraConfig konfigurasi default
func DefaultAuraConfig() AuraConfig {
	return AuraConfig{
		WALDir:        ".omni/wal",
		MaxWorkers:    4,
		RetryDelay:    5 * time.Second,
		MaxRetries:    3,
		FlushInterval: 100 * time.Millisecond,
	}
}

// AuraEngine mesin queue persisten
type AuraEngine struct {
	config    AuraConfig
	queue     chan *AuraJob
	handlers  map[string]JobHandler
	walFile   *os.File
	walMu     sync.Mutex
	running   atomic.Bool
	stats     AuraStats
	mu        sync.RWMutex
}

// AuraStats statistik queue
type AuraStats struct {
	TotalDispatched atomic.Int64
	TotalProcessed  atomic.Int64
	TotalFailed     atomic.Int64
	TotalRetried    atomic.Int64
	QueueDepth      atomic.Int64
}

// JobHandler fungsi yang memproses job
type JobHandler func(job *AuraJob) error

// IgniteAura menyalakan mesin queue abadi
func IgniteAura(config AuraConfig) (*AuraEngine, error) {
	log.Println("💾 [OMNI-AURA] Menyalakan Immortal Queue Engine...")

	// Buat direktori WAL jika belum ada
	if err := os.MkdirAll(config.WALDir, 0755); err != nil {
		return nil, fmt.Errorf("gagal membuat WAL dir: %w", err)
	}

	// Buka WAL file (append mode — tulis di ujung, tidak pernah overwrite)
	walPath := filepath.Join(config.WALDir, "omni_wal.jsonl")
	walFile, err := os.OpenFile(walPath, os.O_CREATE|os.O_APPEND|os.O_RDWR, 0644)
	if err != nil {
		return nil, fmt.Errorf("gagal membuka WAL file: %w", err)
	}

	engine := &AuraEngine{
		config:   config,
		queue:    make(chan *AuraJob, 10000), // Buffer 10K jobs
		handlers: make(map[string]JobHandler),
		walFile:  walFile,
	}

	engine.running.Store(true)

	// Replay WAL: baca job yang belum selesai dari crash sebelumnya
	recovered := engine.replayWAL()
	if recovered > 0 {
		log.Printf("🔮 [OMNI-AURA] %d job ditemukan di WAL! Melanjutkan eksekusi...", recovered)
	}

	// Lahirkan worker consumers
	for i := 0; i < config.MaxWorkers; i++ {
		go engine.consumer(i + 1)
	}

	log.Printf("💾 [OMNI-AURA] Queue Engine ONLINE — %d workers, WAL: %s",
		config.MaxWorkers, walPath)

	return engine, nil
}

// RegisterHandler mendaftarkan handler untuk jenis job tertentu
func (e *AuraEngine) RegisterHandler(jobName string, handler JobHandler) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.handlers[jobName] = handler
	log.Printf("   📋 [AURA] Handler terdaftar: %s", jobName)
}

// Dispatch menambahkan job ke queue + menulis ke WAL
func (e *AuraEngine) Dispatch(name string, payload map[string]interface{}) (string, error) {
	job := &AuraJob{
		ID:        fmt.Sprintf("job_%d_%d", time.Now().UnixNano(), e.stats.TotalDispatched.Load()),
		Name:      name,
		Payload:   payload,
		Status:    "pending",
		MaxRetry:  e.config.MaxRetries,
		CreatedAt: time.Now().Unix(),
		UpdatedAt: time.Now().Unix(),
	}

	// LANGKAH KRITIS: Tulis ke WAL SEBELUM memasukkan ke queue
	// Ini menjamin jika server mati SEKARANG, job bisa di-replay
	if err := e.writeWAL(job); err != nil {
		return "", fmt.Errorf("gagal menulis WAL: %w", err)
	}

	// Masukkan ke queue channel
	e.queue <- job
	e.stats.TotalDispatched.Add(1)
	e.stats.QueueDepth.Add(1)

	log.Printf("📥 [AURA] Job dispatched: %s (%s)", job.Name, job.ID)
	return job.ID, nil
}

// consumer worker yang memproses job dari queue
func (e *AuraEngine) consumer(workerID int) {
	log.Printf("   👷 [AURA-WORKER-%d] Consumer ONLINE", workerID)

	for job := range e.queue {
		if !e.running.Load() {
			return
		}

		e.mu.RLock()
		handler, exists := e.handlers[job.Name]
		e.mu.RUnlock()

		if !exists {
			log.Printf("⚠️ [AURA-WORKER-%d] Tidak ada handler untuk job: %s", workerID, job.Name)
			e.stats.TotalFailed.Add(1)
			e.stats.QueueDepth.Add(-1)
			continue
		}

		// Proses job
		job.Status = "processing"
		job.UpdatedAt = time.Now().Unix()

		err := handler(job)
		if err != nil {
			job.Error = err.Error()
			job.Retries++

			if job.Retries <= job.MaxRetry {
				// Retry setelah delay
				log.Printf("🔄 [AURA-WORKER-%d] Job %s gagal, retry %d/%d: %v",
					workerID, job.ID, job.Retries, job.MaxRetry, err)
				e.stats.TotalRetried.Add(1)
				time.Sleep(e.config.RetryDelay)
				e.queue <- job // kembali ke queue
				continue
			}

			// Menyerah — terlalu banyak retry
			job.Status = "failed"
			e.stats.TotalFailed.Add(1)
			log.Printf("💀 [AURA-WORKER-%d] Job %s GAGAL PERMANEN setelah %d retry",
				workerID, job.ID, job.Retries)
		} else {
			job.Status = "done"
			e.stats.TotalProcessed.Add(1)
			log.Printf("✅ [AURA-WORKER-%d] Job %s selesai!", workerID, job.ID)
		}

		e.stats.QueueDepth.Add(-1)
		// Update WAL status
		_ = e.writeWAL(job)
	}
}

// writeWAL menulis satu entry ke file WAL (append, crash-safe)
func (e *AuraEngine) writeWAL(job *AuraJob) error {
	e.walMu.Lock()
	defer e.walMu.Unlock()

	data, err := json.Marshal(job)
	if err != nil {
		return err
	}

	// Append newline-delimited JSON
	_, err = e.walFile.Write(append(data, '\n'))
	if err != nil {
		return err
	}

	// fsync untuk memastikan data benar-benar sampai ke SSD
	return e.walFile.Sync()
}

// replayWAL membaca WAL dan memasukkan job yang belum selesai kembali ke queue
func (e *AuraEngine) replayWAL() int {
	walPath := filepath.Join(e.config.WALDir, "omni_wal.jsonl")

	data, err := os.ReadFile(walPath)
	if err != nil || len(data) == 0 {
		return 0
	}

	// Parse JSONL (satu job per baris)
	recovered := 0
	jobMap := make(map[string]*AuraJob) // Track latest status per job ID

	lines := splitLines(data)
	for _, line := range lines {
		if len(line) == 0 {
			continue
		}
		var job AuraJob
		if err := json.Unmarshal(line, &job); err != nil {
			continue
		}
		jobMap[job.ID] = &job
	}

	// Re-queue job yang masih pending atau processing (belum done/failed)
	for _, job := range jobMap {
		if job.Status == "pending" || job.Status == "processing" {
			job.Status = "pending" // Reset ke pending untuk re-process
			e.queue <- job
			recovered++
		}
	}

	return recovered
}

// splitLines memecah byte slice menjadi baris-baris
func splitLines(data []byte) [][]byte {
	var lines [][]byte
	start := 0
	for i, b := range data {
		if b == '\n' {
			if i > start {
				lines = append(lines, data[start:i])
			}
			start = i + 1
		}
	}
	if start < len(data) {
		lines = append(lines, data[start:])
	}
	return lines
}

// GetAuraStats mengembalikan statistik queue
func (e *AuraEngine) GetAuraStats() map[string]interface{} {
	return map[string]interface{}{
		"total_dispatched": e.stats.TotalDispatched.Load(),
		"total_processed":  e.stats.TotalProcessed.Load(),
		"total_failed":     e.stats.TotalFailed.Load(),
		"total_retried":    e.stats.TotalRetried.Load(),
		"queue_depth":      e.stats.QueueDepth.Load(),
		"max_workers":      e.config.MaxWorkers,
		"wal_dir":          e.config.WALDir,
	}
}

// Shutdown menghentikan engine dengan graceful
func (e *AuraEngine) Shutdown() {
	log.Println("🛑 [OMNI-AURA] Menghentikan Queue Engine...")
	e.running.Store(false)
	close(e.queue)
	e.walFile.Close()
	log.Println("✅ [OMNI-AURA] Queue Engine dihentikan, WAL aman di SSD.")
}
