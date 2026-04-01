package engine

import (
	"fmt"
	"sync"
	"time"
)

// ==========================================
// ⏳ ASYNC JOB TRACKER: PENCEGAH TIMEOUT BROWSER
// ==========================================
// Saat file 50GB diproses (30+ menit), browser akan timeout
// jika kita suruh menunggu. Maka kita harus:
// 1. Terima file & masukkan ke antrean
// 2. Langsung balas: "ID Tugas Anda #999"
// 3. Browser polling: "Tugas #999 sudah selesai?"
// 4. Setelah selesai: "Tugas #999 DONE. Download di sini."
// ==========================================

// JobStatus merepresentasikan status satu pekerjaan async
type JobStatus struct {
	ID         string    `json:"id"`
	ToolID     string    `json:"tool_id"`
	Status     string    `json:"status"`   // "queued", "processing", "done", "failed"
	Progress   int       `json:"progress"` // 0-100
	Message    string    `json:"message"`
	InputFile  string    `json:"input_file"`
	OutputFile string    `json:"output_file,omitempty"`
	Error      string    `json:"error,omitempty"`
	CreatedAt  time.Time `json:"created_at"`
	StartedAt  time.Time `json:"started_at,omitempty"`
	FinishedAt time.Time `json:"finished_at,omitempty"`
	Duration   string    `json:"duration,omitempty"`
}

// AsyncJobTracker mengelola semua pekerjaan async di memori
type AsyncJobTracker struct {
	mu   sync.RWMutex
	jobs map[string]*JobStatus
}

// Global instance
var Tracker = &AsyncJobTracker{
	jobs: make(map[string]*JobStatus),
}

// ==========================================
// MEMBUAT PEKERJAAN BARU
// ==========================================

// CreateJob mendaftarkan pekerjaan baru dan mengembalikan ID-nya
func (t *AsyncJobTracker) CreateJob(toolID, inputFile string) string {
	t.mu.Lock()
	defer t.mu.Unlock()

	jobID := fmt.Sprintf("JOB-%d", time.Now().UnixNano())
	t.jobs[jobID] = &JobStatus{
		ID:        jobID,
		ToolID:    toolID,
		Status:    "queued",
		Progress:  0,
		Message:   "Tugas sedang dalam antrean...",
		InputFile: inputFile,
		CreatedAt: time.Now(),
	}

	return jobID
}

// ==========================================
// UPDATE STATUS PEKERJAAN
// ==========================================

// MarkProcessing menandai pekerjaan sedang diproses
func (t *AsyncJobTracker) MarkProcessing(jobID string) {
	t.mu.Lock()
	defer t.mu.Unlock()

	if job, ok := t.jobs[jobID]; ok {
		job.Status = "processing"
		job.StartedAt = time.Now()
		job.Message = "Pemrosesan sedang berlangsung..."
	}
}

// UpdateProgress memperbarui persentase progress
func (t *AsyncJobTracker) UpdateProgress(jobID string, progress int, message string) {
	t.mu.Lock()
	defer t.mu.Unlock()

	if job, ok := t.jobs[jobID]; ok {
		job.Progress = progress
		if message != "" {
			job.Message = message
		}
	}
}

// MarkDone menandai pekerjaan selesai dengan file output
func (t *AsyncJobTracker) MarkDone(jobID, outputFile string) {
	t.mu.Lock()
	defer t.mu.Unlock()

	if job, ok := t.jobs[jobID]; ok {
		job.Status = "done"
		job.Progress = 100
		job.OutputFile = outputFile
		job.FinishedAt = time.Now()
		job.Duration = job.FinishedAt.Sub(job.StartedAt).String()
		job.Message = "Selesai! File siap diunduh."
	}
}

// MarkFailed menandai pekerjaan gagal
func (t *AsyncJobTracker) MarkFailed(jobID, errorMsg string) {
	t.mu.Lock()
	defer t.mu.Unlock()

	if job, ok := t.jobs[jobID]; ok {
		job.Status = "failed"
		job.FinishedAt = time.Now()
		job.Duration = job.FinishedAt.Sub(job.StartedAt).String()
		job.Error = errorMsg
		job.Message = "Gagal: " + errorMsg
	}
}

// ==========================================
// MEMBACA STATUS PEKERJAAN (Untuk Polling API)
// ==========================================

// GetJob mengembalikan status pekerjaan berdasarkan ID
func (t *AsyncJobTracker) GetJob(jobID string) (*JobStatus, bool) {
	t.mu.RLock()
	defer t.mu.RUnlock()

	job, ok := t.jobs[jobID]
	if !ok {
		return nil, false
	}
	// Return salinan agar tidak ada race condition
	copy := *job
	return &copy, true
}

// GetAllJobs mengembalikan semua pekerjaan (untuk monitoring dashboard)
func (t *AsyncJobTracker) GetAllJobs() []*JobStatus {
	t.mu.RLock()
	defer t.mu.RUnlock()

	result := make([]*JobStatus, 0, len(t.jobs))
	for _, job := range t.jobs {
		copy := *job
		result = append(result, &copy)
	}
	return result
}

// ==========================================
// CLEANUP: Hapus pekerjaan lama (> 24 jam)
// ==========================================

// CleanupOldJobs menghapus pekerjaan yang sudah lebih dari maxAge
func (t *AsyncJobTracker) CleanupOldJobs(maxAge time.Duration) int {
	t.mu.Lock()
	defer t.mu.Unlock()

	count := 0
	cutoff := time.Now().Add(-maxAge)
	for id, job := range t.jobs {
		if job.CreatedAt.Before(cutoff) && (job.Status == "done" || job.Status == "failed") {
			delete(t.jobs, id)
			count++
		}
	}
	return count
}

// StartCleanupWorker menjalankan goroutine yang membersihkan pekerjaan lama setiap interval
func (t *AsyncJobTracker) StartCleanupWorker(interval, maxAge time.Duration) {
	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()
		for range ticker.C {
			cleaned := t.CleanupOldJobs(maxAge)
			if cleaned > 0 {
				fmt.Printf("🧹 [JOB TRACKER] Dibersihkan %d pekerjaan lama.\n", cleaned)
			}
		}
	}()
}
