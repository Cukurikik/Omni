package core

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"runtime"
	"sync"
	"time"
)

// ==========================================
// 🔬 OMNI-DEV: TRANSPARENT DEBUGGING MODE
// ==========================================
// Saat mode development aktif, OMNI menjadi transparan seperti kaca:
// - Setiap request HTTP ditampilkan dengan durasi eksekusi
// - Setiap job menampilkan fase-fase internal (decode, process, encode)
// - Memory usage / goroutine count selalu visible
// - Endpoint /api/v1/dev/inspect memberikan snapshot sistem real-time
//
// Filosofi: Menerangi Black Box.
//   Selama development, developer tidak boleh menebak-nebak.
//   Setiap nanosecond harus terukur, setiap goroutine harus terlihat.
//
// Aktivasi:
//   - appconfig.json → environment: "development"
//   - Otomatis aktif saat `omni dev` dijalankan
//   - Otomatis MATI saat `omni build` (production mode)
// ==========================================

// DevMode adalah flag global — true jika environment == "development"
var DevMode bool

// InitDevMode membaca appconfig dan mengaktifkan mode debugging jika development
func InitDevMode() {
	if AppConfig == nil {
		return
	}

	DevMode = AppConfig.Environment == "development"

	if DevMode {
		log.Println("🔬 [OMNI-DEV] ==========================================")
		log.Println("🔬 [OMNI-DEV] TRANSPARENT DEBUGGING MODE: AKTIF")
		log.Println("🔬 [OMNI-DEV] Semua request, job, dan memory termonitor!")
		log.Println("🔬 [OMNI-DEV] Endpoint: /api/v1/dev/inspect")
		log.Println("🔬 [OMNI-DEV] ==========================================")
	}
}

// ==========================================
// 📊 REQUEST PROFILER: Ukur Durasi Setiap Request
// ==========================================

// DevProfileMiddleware membungkus HTTP handler dengan profiling waktu eksekusi.
// Hanya aktif saat DevMode = true. Di production, ini pass-through murni.
func DevProfileMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !DevMode {
			next.ServeHTTP(w, r)
			return
		}

		start := time.Now()

		// Tangkap status code menggunakan wrapper
		ww := &statusWriter{ResponseWriter: w, statusCode: 200}
		next.ServeHTTP(ww, r)

		duration := time.Since(start)

		// Warna berdasarkan durasi
		emoji := "🟢"
		if duration > 500*time.Millisecond {
			emoji = "🟡"
		}
		if duration > 2*time.Second {
			emoji = "🔴"
		}

		log.Printf("%s [DEV-PROFILE] %s %s → %d | %s | Goroutines: %d",
			emoji, r.Method, r.URL.Path, ww.statusCode, duration, runtime.NumGoroutine())

		// Catat ke profiler
		recordProfile(r.Method, r.URL.Path, ww.statusCode, duration)
	})
}

type statusWriter struct {
	http.ResponseWriter
	statusCode int
}

func (w *statusWriter) WriteHeader(code int) {
	w.statusCode = code
	w.ResponseWriter.WriteHeader(code)
}

// ==========================================
// 📈 PROFILING DATA: Menyimpan Metrik Request
// ==========================================

type profileEntry struct {
	Method   string        `json:"method"`
	Path     string        `json:"path"`
	Status   int           `json:"status"`
	Duration string        `json:"duration"`
	Time     time.Time     `json:"time"`
	DurationNs int64       `json:"duration_ns"`
}

var (
	profileMu      sync.Mutex
	profileHistory []profileEntry
	maxProfileSize = 100 // Simpan 100 request terakhir
)

func recordProfile(method, path string, status int, dur time.Duration) {
	profileMu.Lock()
	defer profileMu.Unlock()

	entry := profileEntry{
		Method:     method,
		Path:       path,
		Status:     status,
		Duration:   dur.String(),
		Time:       time.Now(),
		DurationNs: dur.Nanoseconds(),
	}

	profileHistory = append(profileHistory, entry)

	// Sliding window — buang yang lama
	if len(profileHistory) > maxProfileSize {
		profileHistory = profileHistory[len(profileHistory)-maxProfileSize:]
	}
}

// ==========================================
// 🔍 SYSTEM INSPECTOR: State Dump Endpoint
// ==========================================

// SystemInspectData adalah snapshot lengkap sistem untuk debugging
type SystemInspectData struct {
	Timestamp     string         `json:"timestamp"`
	Environment   string         `json:"environment"`
	DevMode       bool           `json:"dev_mode"`
	GoVersion     string         `json:"go_version"`
	NumCPU        int            `json:"num_cpu"`
	NumGoroutine  int            `json:"num_goroutine"`
	Memory        MemorySnapshot `json:"memory"`
	Adapters      []AdapterStatus `json:"adapters"`
	JobListeners  int            `json:"active_job_listeners"`
	RecentRequests []profileEntry `json:"recent_requests"`
}

type MemorySnapshot struct {
	AllocMB      float64 `json:"alloc_mb"`
	TotalAllocMB float64 `json:"total_alloc_mb"`
	SysMB        float64 `json:"sys_mb"`
	NumGC        uint32  `json:"num_gc"`
	HeapObjects  uint64  `json:"heap_objects"`
}

// DevInspectHandler menyajikan snapshot lengkap sistem untuk debugging.
// Route: /api/v1/dev/inspect
//
// HANYA AKTIF saat DevMode = true. Di production, endpoint ini mengembalikan 403.
func DevInspectHandler(w http.ResponseWriter, r *http.Request) {
	if !DevMode {
		http.Error(w, `{"error":"OMNI-DEV inspection hanya tersedia di mode development"}`, http.StatusForbidden)
		return
	}

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Ambil profiling history
	profileMu.Lock()
	recentReqs := make([]profileEntry, len(profileHistory))
	copy(recentReqs, profileHistory)
	profileMu.Unlock()

	data := SystemInspectData{
		Timestamp:    time.Now().Format(time.RFC3339),
		Environment:  AppConfig.Environment,
		DevMode:      DevMode,
		GoVersion:    runtime.Version(),
		NumCPU:       runtime.NumCPU(),
		NumGoroutine: runtime.NumGoroutine(),
		Memory: MemorySnapshot{
			AllocMB:      float64(memStats.Alloc) / (1024 * 1024),
			TotalAllocMB: float64(memStats.TotalAlloc) / (1024 * 1024),
			SysMB:        float64(memStats.Sys) / (1024 * 1024),
			NumGC:        memStats.NumGC,
			HeapObjects:  memStats.HeapObjects,
		},
		Adapters:       CheckAllAdapters(),
		JobListeners:   GetActiveListeners(),
		RecentRequests: recentReqs,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

// ==========================================
// 🐛 JOB TRACER: Fase-Fase Internal Job
// ==========================================

// DevTrace menulis log debugging detail hanya saat DevMode aktif.
// Di production, fungsi ini tidak melakukan apa-apa (zero cost).
//
// Contoh:
//
//	core.DevTrace("JOB-123", "DECODE", "Memulai decode frame video ke-1024...")
//	core.DevTrace("JOB-123", "PROCESS", "Filter hqdn3d diterapkan. Duration: 145ms")
//	core.DevTrace("JOB-123", "ENCODE", "Re-encoding selesai. Output: 2.3GB")
func DevTrace(jobID string, phase string, message string) {
	if !DevMode {
		return
	}
	log.Printf("🐛 [JOB-TRACE] [%s] [%s] %s", jobID, phase, message)
}

// DevTraceF adalah DevTrace dengan format string
func DevTraceF(jobID string, phase string, format string, args ...interface{}) {
	if !DevMode {
		return
	}
	msg := fmt.Sprintf(format, args...)
	log.Printf("🐛 [JOB-TRACE] [%s] [%s] %s", jobID, phase, msg)
}

// DevMemReport mencetak snapshot memori singkat ke log (untuk debugging memory leak)
func DevMemReport(label string) {
	if !DevMode {
		return
	}
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	log.Printf("🧠 [DEV-MEM] [%s] Alloc=%.2fMB | Sys=%.2fMB | Goroutines=%d | HeapObj=%d",
		label,
		float64(m.Alloc)/(1024*1024),
		float64(m.Sys)/(1024*1024),
		runtime.NumGoroutine(),
		m.HeapObjects,
	)
}
