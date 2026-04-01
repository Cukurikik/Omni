package services

import (
	"omnitools/core"
	"fmt"
	"strings"
	"sync"
	"time"
)

// ==========================================
// KONFIGURASI SMART PRIORITY (Multi-Lane)
// ==========================================
// Mengganti konsep "Satu Antrean Kaku" menjadi "Tiga Jalur Cerdas" (The Fair Manager)
const (
	MaxFastWorkers = 8   // Pekerja untuk Gambar & Metadata (< 5 detik)
	MaxFastQueue   = 200 // Kapasitas antrean jalur cepat

	MaxMediumWorkers = 4   // Pekerja untuk Audio & PDF ringan (< 1 menit)
	MaxMediumQueue   = 100 // Kapasitas antrean jalur menengah

	MaxHeavyWorkers = 2  // Pekerja untuk Video & AI Berat (> 1 menit)
	MaxHeavyQueue   = 50 // Kapasitas antrean jalur berat
)

// ==========================================
// STRUKTUR DATA PEKERJAAN
// ==========================================
// PIPA ANTREAN GANDA (Fast, Medium, Heavy)
// ==========================================
var (
	FastQueue   = make(chan core.Job, MaxFastQueue)
	MediumQueue = make(chan core.Job, MaxMediumQueue)
	HeavyQueue  = make(chan core.Job, MaxHeavyQueue)

	wg sync.WaitGroup
)

// ==========================================
// MENYALAKAN PABRIK PEKERJA JALUR GANDA
// ==========================================
func StartWorkerPool() {
	WriteLog("SYSTEM", "INFO_CLUSTER", fmt.Sprintf("🚥 THE FAIR MANAGER Menyala! Pekerja: FAST(%d), MED(%d), HVY(%d)", MaxFastWorkers, MaxMediumWorkers, MaxHeavyWorkers))

	for i := 1; i <= MaxFastWorkers; i++ {
		wg.Add(1)
		go worker(i, "FAST", FastQueue)
	}

	for i := 1; i <= MaxMediumWorkers; i++ {
		wg.Add(1)
		go worker(i, "MEDIUM", MediumQueue)
	}

	for i := 1; i <= MaxHeavyWorkers; i++ {
		wg.Add(1)
		go worker(i, "HEAVY", HeavyQueue)
	}
}

// ==========================================
// LOGIKA SANG PEKERJA (Pekerja Lajur Khusus)
// ==========================================
func worker(workerID int, lane string, jobs <-chan core.Job) {
	defer wg.Done()
	for job := range jobs {
		startTime := time.Now()
		WriteLog("QUEUE", "INFO_JOB_START", fmt.Sprintf("[JALUR %s] Pekerja #%d mengeksekusi [%s]", lane, workerID, job.ID))

		timeout := job.Timeout
		if timeout == 0 {
			timeout = 5 * time.Minute
		}

		// Panggil Master Orchestrator (Dependency Injection)
		out, err := core.ExecuteTool(&job)
		duration := time.Since(startTime)

		if job.Result != nil {
			job.Result <- core.JobResult{
				Success: err == nil,
				Data:    out,
				Error:   err,
			}
		}

		if err != nil {
			WriteLog("QUEUE", "ERR_JOB_FAIL", fmt.Sprintf("[JALUR %s] Pekerja #%d GAGAL pada [%s] (%v): %v", lane, workerID, job.ID, duration, err))
		} else {
			WriteLog("QUEUE", "INFO_JOB_DONE", fmt.Sprintf("[JALUR %s] Pekerja #%d SELESAI [%s] dalam %v", lane, workerID, job.ID, duration))
		}

		// ⚡ OMNI-AURA: TUGAS SELESAI, HAPUS DARI DAFTAR TUNGGU WAL!
		WriteToWAL("DEQUEUE", &job)
	}
}

// ==========================================
// PENENTU JALUR OTOMATIS BERDASARKAN ID
// ==========================================
func GetPriorityLane(toolID string) string {
	if strings.HasPrefix(toolID, "image_") || strings.HasPrefix(toolID, "converter_") || strings.HasPrefix(toolID, "md_") {
		return "FAST"
	}
	if strings.HasPrefix(toolID, "audio_") || strings.HasPrefix(toolID, "pdf_") {
		return "MEDIUM"
	}
	return "HEAVY" // Termasuk video_, ai_, dan alat raksasa lainnya
}

// ==========================================
// SUBMIT PEKERJAAN DENGAN TIMEOUT
// ==========================================
func SubmitJobWithTimeout(toolID string, engineCmd string, args []string, timeout time.Duration) core.JobResult {
	lane := GetPriorityLane(toolID)
	resultChan := make(chan core.JobResult, 1)

	job := core.Job{
		ID:        fmt.Sprintf("JOB-%d", time.Now().UnixNano()),
		Category:  lane,
		EngineCmd: engineCmd,
		Args:      args,
		Timeout:   timeout,
		Result:    resultChan, // Tidak di JSON-kan (karena channel)
	}

	// ⚡ OMNI-AURA: CATAT KE SSD SEBELUM MASUK RAM!
	WriteToWAL("ENQUEUE", &job)

	switch lane {
	case "FAST":
		select {
		case FastQueue <- job:
			WriteLog("QUEUE", "INFO_QUEUED", fmt.Sprintf("✈️  [JALUR %s] Tugas [%s] antre.", lane, job.ID))
			return <-resultChan
		default:
			return core.JobResult{Success: false, Error: fmt.Errorf("Jalur Cepat penuh (%d/%d)", MaxFastQueue, MaxFastQueue)}
		}
	case "MEDIUM":
		select {
		case MediumQueue <- job:
			WriteLog("QUEUE", "INFO_QUEUED", fmt.Sprintf("🚗 [JALUR %s] Tugas [%s] antre.", lane, job.ID))
			return <-resultChan
		default:
			return core.JobResult{Success: false, Error: fmt.Errorf("Jalur Menengah penuh (%d/%d)", MaxMediumQueue, MaxMediumQueue)}
		}
	default: // HEAVY
		select {
		case HeavyQueue <- job:
			WriteLog("QUEUE", "INFO_QUEUED", fmt.Sprintf("🚚 [JALUR %s] Tugas [%s] antre.", lane, job.ID))
			return <-resultChan
		default:
			return core.JobResult{Success: false, Error: fmt.Errorf("Jalur Berat penuh (%d/%d)", MaxHeavyQueue, MaxHeavyQueue)}
		}
	}
}

// ==========================================
// SUBMIT PEKERJAAN (DEFAULT 5 MENIT)
// ==========================================
func SubmitJob(toolID string, engineCmd string, args []string) core.JobResult {
	return SubmitJobWithTimeout(toolID, engineCmd, args, 5*time.Minute)
}
