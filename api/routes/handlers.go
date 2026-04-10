package routes

import (
	"fmt"
	"net/http"
	"runtime"
	"time"

	"omnitools/core"
)

// ==========================================
// 📈 PROMETHEUS METRICS: ENTERPRISE TELEMETRY V1.3
// ==========================================
// Prometheus Scraper membaca endpoint ini setiap 5-15 detik.
// Format: OpenMetrics / Prometheus Exposition Format v0.0.4
//
// Kubernetes HPA akan menggunakan metrik ini untuk auto-scaling:
//   - omni_active_jobs > 10 → scale up worker pods
//   - omni_memory_alloc_bytes > 1GB → alert
//   - omni_http_duration_ms_avg > 500 → degrade gracefully
//
// Route: GET /api/v1/omni/metrics
// ==========================================

var (
	serverStartTime  = time.Now()
	totalHTTPRequests int64
)

// IncrementHTTPCounter dipanggil oleh middleware setiap request masuk
func IncrementHTTPCounter() {
	totalHTTPRequests++
}

func MetricsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	activeJobs := core.GetCurrentActiveJobs()
	uptimeSeconds := int64(time.Since(serverStartTime).Seconds())
	goroutines := runtime.NumGoroutine()
	sseListeners := core.GetActiveSSEListeners()
	adapterCount := core.GetAdapterCount()

	// Bangun metrik dalam format Prometheus Exposition
	metrics := ""

	// === Job Metrics ===
	metrics += "# HELP omni_active_jobs Jumlah tugas yang sedang berjalan\n"
	metrics += "# TYPE omni_active_jobs gauge\n"
	metrics += fmt.Sprintf("omni_active_jobs %d\n", activeJobs)

	// === Uptime ===
	metrics += "# HELP omni_uptime_seconds Detik sejak server dinyalakan\n"
	metrics += "# TYPE omni_uptime_seconds counter\n"
	metrics += fmt.Sprintf("omni_uptime_seconds %d\n", uptimeSeconds)

	// === HTTP Requests ===
	metrics += "# HELP omni_http_requests_total Total HTTP requests yang diterima\n"
	metrics += "# TYPE omni_http_requests_total counter\n"
	metrics += fmt.Sprintf("omni_http_requests_total %d\n", totalHTTPRequests)

	// === Goroutines ===
	metrics += "# HELP omni_goroutines Jumlah goroutine aktif\n"
	metrics += "# TYPE omni_goroutines gauge\n"
	metrics += fmt.Sprintf("omni_goroutines %d\n", goroutines)

	// === Memory Metrics ===
	metrics += "# HELP omni_memory_alloc_bytes RAM yang sedang terpakai (bytes)\n"
	metrics += "# TYPE omni_memory_alloc_bytes gauge\n"
	metrics += fmt.Sprintf("omni_memory_alloc_bytes %d\n", memStats.Alloc)

	metrics += "# HELP omni_memory_sys_bytes Total RAM yang di-request dari OS (bytes)\n"
	metrics += "# TYPE omni_memory_sys_bytes gauge\n"
	metrics += fmt.Sprintf("omni_memory_sys_bytes %d\n", memStats.Sys)

	metrics += "# HELP omni_memory_heap_objects Jumlah objek di heap\n"
	metrics += "# TYPE omni_memory_heap_objects gauge\n"
	metrics += fmt.Sprintf("omni_memory_heap_objects %d\n", memStats.HeapObjects)

	metrics += "# HELP omni_gc_cycles_total Total siklus Garbage Collection\n"
	metrics += "# TYPE omni_gc_cycles_total counter\n"
	metrics += fmt.Sprintf("omni_gc_cycles_total %d\n", memStats.NumGC)

	metrics += "# HELP omni_gc_pause_ns_total Total waktu pause GC (nanoseconds)\n"
	metrics += "# TYPE omni_gc_pause_ns_total counter\n"
	metrics += fmt.Sprintf("omni_gc_pause_ns_total %d\n", memStats.PauseTotalNs)

	// === SSE Metrics ===
	metrics += "# HELP omni_sse_listeners Jumlah SSE listener aktif\n"
	metrics += "# TYPE omni_sse_listeners gauge\n"
	metrics += fmt.Sprintf("omni_sse_listeners %d\n", sseListeners)

	// === Adapter Metrics ===
	metrics += "# HELP omni_adapter_total Jumlah adapter terdaftar\n"
	metrics += "# TYPE omni_adapter_total gauge\n"
	metrics += fmt.Sprintf("omni_adapter_total %d\n", adapterCount)

	// Per-adapter status (1=active, 0=down)
	adapters := core.CheckAllAdapters()
	metrics += "# HELP omni_adapter_status Status adapter (1=active, 0=down)\n"
	metrics += "# TYPE omni_adapter_status gauge\n"
	for _, a := range adapters {
		val := 0
		if a.State == core.AdapterActive {
			val = 1
		}
		metrics += fmt.Sprintf("omni_adapter_status{name=\"%s\"} %d\n", a.Name, val)
	}

	// === OMNI-TITAN Buffer Pool Metrics ===
	metrics += "# HELP omni_titan_buffer_bytes Kapasitas buffer per slot OMNI-TITAN\n"
	metrics += "# TYPE omni_titan_buffer_bytes gauge\n"
	metrics += fmt.Sprintf("omni_titan_buffer_bytes %d\n", core.GetTitanCapacityBytes()) // 10GB

	metrics += "# HELP omni_titan_max_pool_bytes Total kapasitas RAM pool Titan (buffer × slots)\n"
	metrics += "# TYPE omni_titan_max_pool_bytes gauge\n"
	metrics += fmt.Sprintf("omni_titan_max_pool_bytes %d\n", core.GetTitanMaxPoolBytes()) // 30GB

	metrics += "# HELP omni_titan_active_slots Slot Titan yang sedang dipakai\n"
	metrics += "# TYPE omni_titan_active_slots gauge\n"
	metrics += fmt.Sprintf("omni_titan_active_slots %d\n", core.GetTitanActiveSlots())

	metrics += "# HELP omni_titan_queue_waiting Goroutine yang mengantre slot Titan\n"
	metrics += "# TYPE omni_titan_queue_waiting gauge\n"
	metrics += fmt.Sprintf("omni_titan_queue_waiting %d\n", core.GetTitanQueueWaiting())

	metrics += "# HELP omni_titan_total_streamed_bytes Total bytes yang telah di-stream oleh Titan\n"
	metrics += "# TYPE omni_titan_total_streamed_bytes counter\n"
	metrics += fmt.Sprintf("omni_titan_total_streamed_bytes %d\n", core.GetTitanTotalStreamed())

	metrics += "# HELP omni_titan_total_batches Total batch write ke SSD oleh Titan\n"
	metrics += "# TYPE omni_titan_total_batches counter\n"
	metrics += fmt.Sprintf("omni_titan_total_batches %d\n", core.GetTitanTotalBatches())

	// === CPU Metrics ===
	metrics += "# HELP omni_cpu_count Jumlah CPU core tersedia\n"
	metrics += "# TYPE omni_cpu_count gauge\n"
	metrics += fmt.Sprintf("omni_cpu_count %d\n", runtime.NumCPU())

	// === Nexus Cluster ===
	if core.AppConfig != nil && core.AppConfig.NexusCluster.Role == "master" {
		workerCount := core.GetRegisteredWorkerCount()
		metrics += "# HELP omni_nexus_workers Jumlah worker nodes terdaftar di cluster\n"
		metrics += "# TYPE omni_nexus_workers gauge\n"
		metrics += fmt.Sprintf("omni_nexus_workers %d\n", workerCount)
	}

	// === OMNI Info (label-style metadata) ===
	appVersion := "unknown"
	environment := "unknown"
	if core.AppConfig != nil {
		appVersion = core.AppConfig.Version
		environment = core.AppConfig.Environment
	}
	metrics += "# HELP omni_info OMNI Framework metadata\n"
	metrics += "# TYPE omni_info gauge\n"
	metrics += fmt.Sprintf("omni_info{version=\"%s\",environment=\"%s\",go_version=\"%s\"} 1\n",
		appVersion, environment, runtime.Version())

	w.Write([]byte(metrics))
}

// JobStatusHandler membalas status terkini dari sebuah tugas
func JobStatusHandler(w http.ResponseWriter, r *http.Request) {
	jobID := r.URL.Query().Get("job_id")
	w.Header().Set("Content-Type", "application/json")

	status := "PROCESSING"

	// Jika OMNI-DB aktif, baca dari database
	if core.DB != nil {
		job, err := core.DB.GetJob(jobID)
		if err == nil {
			status = job.Status
		}
	}

	w.Write([]byte(`{"job_id": "` + jobID + `", "status": "` + status + `"}`))
}

