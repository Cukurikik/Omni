package services

import (
	"fmt"
	"sync"
	"time"
)

// ==========================================
// INOVASI #3: PEKERJA INTERNAL GOLANG
// ==========================================
// Berbeda dengan Worker Pool utama yang memanggil C++/Python via exec.Command,
// Golang Internal Worker menjalankan fungsi Go MURNI (goroutine) untuk
// memproses tugas PDF dan Converter tanpa memanggil program eksternal.
//
// Keuntungan:
// - Tidak ada overhead spawn process (0ms startup vs ~50ms exec.Command)
// - Bisa memanfaatkan goroutine ringan (2KB stack vs ~8MB process)
// - Cocok untuk tugas I/O-bound (PDF merge, JSON convert, encoding)

// ==========================================
// KONFIGURASI PEKERJA GOLANG INTERNAL
// ==========================================
const (
	MaxGoWorkers = 8   // Lebih banyak karena goroutine sangat ringan (2KB)
	MaxGoQueue   = 200 // Kapasitas antrean lebih besar karena overhead kecil
)

// ==========================================
// TIPE PEKERJAAN INTERNAL GOLANG
// ==========================================

// GoJobFunc adalah tipe fungsi yang akan dieksekusi oleh pekerja Golang
// Ini menerima path file input dan parameter tambahan, mengembalikan output byte + error
type GoJobFunc func(inputPath string, params map[string]string) ([]byte, error)

// GoJob merepresentasikan satu tugas yang dikerjakan oleh goroutine Golang murni
type GoJob struct {
	ID        string            // Identitas unik
	TaskName  string            // Nama tugas (misal: "pdf_merge", "json_to_xml")
	InputPath string            // Path file dari karantina
	Params    map[string]string // Parameter tambahan dari extraInputs
	Handler   GoJobFunc         // Fungsi Go yang akan dieksekusi
	Result    chan GoJobResult  // Pipa hasil
}

// GoJobResult adalah hasil dari pekerjaan internal Golang
type GoJobResult struct {
	Success    bool
	Data       []byte
	OutputPath string // Path file hasil (di /omni_cache/)
	Error      error
}

// ==========================================
// PIPA ANTREAN GOLANG INTERNAL
// ==========================================
var (
	GoJobQueue = make(chan GoJob, MaxGoQueue)
	goWg       sync.WaitGroup
)

// ==========================================
// MENYALAKAN PABRIK PEKERJA GOLANG
// ==========================================
// StartGoWorkerPool menghidupkan pool goroutine untuk tugas PDF & Converter.
// Panggil di main.go: go services.StartGoWorkerPool()
func StartGoWorkerPool() {
	WriteLog("SYSTEM", "INFO_GO_POOL", fmt.Sprintf("🏗️ Pabrik Pekerja Golang menyala: %d Pekerja Golang, %d Slot Antrean.", MaxGoWorkers, MaxGoQueue))
	for i := 1; i <= MaxGoWorkers; i++ {
		goWg.Add(1)
		go goWorker(i, GoJobQueue)
	}
}

// ==========================================
// LOGIKA PEKERJA GOLANG INTERNAL
// ==========================================
func goWorker(workerID int, jobs <-chan GoJob) {
	defer goWg.Done()
	for job := range jobs {
		startTime := time.Now()
		WriteLog("GO_POOL", "INFO_JOB_START", fmt.Sprintf("GoWorker #%d mengambil tugas [%s] — %s", workerID, job.ID, job.TaskName))

		// Eksekusi fungsi Go murni (bukan exec.Command!)
		output, err := job.Handler(job.InputPath, job.Params)

		duration := time.Since(startTime)

		// Kirim hasil kembali melalui channel
		job.Result <- GoJobResult{
			Success: err == nil,
			Data:    output,
			Error:   err,
		}

		if err != nil {
			WriteLog("GO_POOL", "ERR_JOB_FAIL", fmt.Sprintf("GoWorker #%d GAGAL [%s](%s) dalam %v: %v", workerID, job.ID, job.TaskName, duration, err))
		} else {
			WriteLog("GO_POOL", "INFO_JOB_DONE", fmt.Sprintf("GoWorker #%d selesai [%s](%s) dalam %v", workerID, job.ID, job.TaskName, duration))
		}
	}
}

// ==========================================
// SUBMIT TUGAS GOLANG (Dipanggil dari Handler API)
// ==========================================
// SubmitGoJob menerima tugas untuk dikerjakan oleh goroutine internal.
// Handler cukup menyediakan fungsi Go (GoJobFunc) yang berisi logika
// pemrosesan PDF/Converter.
func SubmitGoJob(taskName string, inputPath string, params map[string]string, handler GoJobFunc) GoJobResult {
	resultChan := make(chan GoJobResult, 1)

	job := GoJob{
		ID:        fmt.Sprintf("GO-%d", time.Now().UnixNano()),
		TaskName:  taskName,
		InputPath: inputPath,
		Params:    params,
		Handler:   handler,
		Result:    resultChan,
	}

	select {
	case GoJobQueue <- job:
		WriteLog("GO_POOL", "INFO_QUEUED", fmt.Sprintf("Tugas [%s](%s) masuk antrean Golang.", job.ID, taskName))
		return <-resultChan
	default:
		WriteLog("GO_POOL", "WARN_QUEUE_FULL", fmt.Sprintf("Antrean Golang penuh (%d/%d). Tugas ditolak!", MaxGoQueue, MaxGoQueue))
		return GoJobResult{
			Success: false,
			Error:   fmt.Errorf("server Golang sibuk, antrean penuh (%d/%d)", MaxGoQueue, MaxGoQueue),
		}
	}
}
