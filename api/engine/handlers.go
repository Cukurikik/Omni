package engine

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"

	"omnitools/core"
	"omnitools/services"
)

// ==========================================
// 🚀 ASYNC PROCESSING HANDLER
// ==========================================
// Endpoint utama untuk 150+ fitur yang memproses file besar.
//
// Alur:
// 1. POST /api/v1/process   → Upload file + masukkan ke antrean → Return Job ID
// 2. GET  /api/v1/job/:id   → Polling status pekerjaan
// 3. GET  /api/v1/download  → Download file hasil pemrosesan
// ==========================================

// ProcessRequest adalah body request untuk memulai pemrosesan
type ProcessRequest struct {
	ToolID  string            `json:"tool_id"`
	Options map[string]string `json:"options"`
}

// AsyncProcessHandler menangani upload file dan memulai pemrosesan async
// Browser langsung mendapat response "Job ID" tanpa menunggu selesai.
//
// 🌐 NEXUS-AWARE: Jika server ini adalah Master, request akan di-stream
// langsung ke Worker yang paling senggang via Zero-RAM Reverse Proxy.
func AsyncProcessHandler(w http.ResponseWriter, r *http.Request) {
	ctx := &core.OmniContext{W: w, R: r}

	if r.Method != http.MethodPost {
		ctx.JSON(405, false, "Method not allowed", nil)
		return
	}

	// ==========================================
	// 🌐 NEXUS PIPELINE: DISTRIBUTED DISPATCH
	// ==========================================

	// 👑 JIKA SERVER INI ADALAH MASTER — Cari Prajurit yang menganggur
	if core.IsNexusMaster() && !core.IsNexusDelegated(r) {
		workerIP, workerNode := core.GetIdleWorker()

		if workerIP != "" {
			// 🔀 PASANG PIPA TEMBUS PANDANG!
			// Data mengalir langsung: User → Master (32KB buffer) → Worker SSD
			// Master tidak menyimpan file ke disk!
			log.Printf("🔀 [NEXUS] Mendelegasikan ke %s (%s) | Load: %d/%d",
				workerIP, workerNode.NodeName, workerNode.ActiveJobs, workerNode.MaxJobs)

			core.StreamToWorker(w, r, workerIP)
			return // Master selesai — response Worker mengalir otomatis ke User
		}

		// Tidak ada Worker tersedia — Master proses sendiri (Standalone Mode)
		log.Printf("⚪ [NEXUS] Tidak ada Worker tersedia — Memproses secara lokal")
	}

	// 🪖 JIKA SERVER INI ADALAH WORKER — Tolak akses langsung dari luar
	if core.IsNexusWorker() && !core.IsNexusDelegated(r) {
		ctx.JSON(403, false, "Akses Langsung Ditolak. Request harus melewati Master Node.", nil)
		return
	}

	// ==========================================
	// 🏭 LOCAL PROCESSING (Worker atau Standalone)
	// ==========================================

	// Track active jobs untuk NEXUS telemetri
	core.IncrementActiveJobs()
	defer core.DecrementActiveJobs()

	// 1. STREAM UPLOAD — Zero-RAM langsung ke SSD
	result, err := core.StreamUpload(r, "incoming")
	if err != nil {
		ctx.JSON(400, false, fmt.Sprintf("Upload gagal: %v", err), nil)
		return
	}

	// 2. Ambil tool_id dari query parameter atau form field
	toolID := r.URL.Query().Get("tool_id")
	if toolID == "" {
		toolID = r.FormValue("tool_id")
	}
	if toolID == "" {
		ctx.JSON(400, false, "tool_id wajib dikirim", nil)
		return
	}

	// 3. DAFTARKAN JOB ASYNC
	jobID := Tracker.CreateJob(toolID, result.FilePath)

	log.Printf("📋 [JOB CREATED] %s → Tool: %s, File: %s (%d MB)",
		jobID, toolID, result.OriginalName, result.Size/(1024*1024))

	// 4. LANGSUNG PROSES DI BACKGROUND (goroutine)
	go processJobAsync(jobID, toolID, result.FilePath, r.URL.Query())

	// 5. LANGSUNG BALAS KE BROWSER — Tidak perlu menunggu!
	ctx.JSON(202, true, "File diterima. Pemrosesan dimulai di latar belakang.", map[string]interface{}{
		"job_id":        jobID,
		"quarantine_id": result.QuarantineID,
		"file_name":     result.OriginalName,
		"file_size":     result.Size,
		"poll_url":      fmt.Sprintf("/api/v1/job?id=%s", jobID),
		"served_by":     core.AppConfig.NexusCluster.Role,
	})
}

// processJobAsync memproses file di background goroutine
// 📡 BROADCASTER terintegrasi: setiap tahap dilaporkan ke browser secara real-time
func processJobAsync(jobID, toolID, inputPath string, queryParams interface{}) {
	Tracker.MarkProcessing(jobID)

	// 📡 SIARAN 1: Pekerjaan dimulai!
	core.BroadcastUpdate(jobID, "PROCESSING", 5, "File diterima. Mempersiapkan mesin render...")

	// 🔥 OMNI-DB: Catat job dimulai ke Firestore
	var inputSize int64
	if fi, err := os.Stat(inputPath); err == nil {
		inputSize = fi.Size()
	}
	core.RecordJobStart(jobID, toolID, filepath.Base(inputPath), inputSize)

	// Siapkan folder output
	cacheDir := filepath.Join("..", "release", "omni_cache")
	os.MkdirAll(cacheDir, 0755)

	// Tentukan output berdasarkan tool
	baseName := filepath.Base(inputPath)
	outputPath := filepath.Join(cacheDir, "out_"+baseName)

	var err error

	// 1. Convert query parameters for the dynamic engine
	dynamicParams := make(map[string]string)
	if q, ok := queryParams.(url.Values); ok {
		for k, v := range q {
			if len(v) > 0 {
				dynamicParams[k] = v[0]
			}
		}
	}

	// 2. Route to engine
	Tracker.UpdateProgress(jobID, 10, "Mengecek pendaftaran alat...")
	core.BroadcastUpdate(jobID, "PROCESSING", 10, "Menganalisa file dan menentukan strategi pemrosesan...")

	switch {
	// === SYSTEM TOOLS (Hardcoded Bypass) ===
	case toolID == "demo_tool":
		core.BroadcastUpdate(jobID, "PROCESSING", 100, "Sanity Check Selesai!")
		err = nil

	// === VIDEO TOOLS (Native Handlers) ===
	case isNativeVideoTool(toolID):
		core.BroadcastUpdate(jobID, "PROCESSING", 15, "Memuat mesin Native Video...")
		switch toolID {
		case "video_thumbnail":
			err = ExtractThumbnail(inputPath, outputPath, "00:00:01")
		case "video_audio_extract":
			err = ExtractAudio(inputPath, outputPath)
		}

	// === ⚡ KINETIC TOOLS (C/C++ Hyper-Engine, Zero Overhead) ===
	// Memproses langsung di memori C tanpa memanggil OS (exec.Command)
	case IsKineticTool(toolID):
		core.BroadcastUpdate(jobID, "PROCESSING", 15, "⚡ Mengaktifkan OMNI-KINETIC C Engine...")

		switch toolID {
		case "kinetic_xor_encrypt":
			xorKey := byte(0x5A) // Default key
			if k, ok := dynamicParams["xor_key"]; ok && len(k) > 0 {
				xorKey = k[0]
			}
			err = KineticXorEncrypt(inputPath, outputPath, xorKey)

		case "kinetic_xor_decrypt":
			xorKey := byte(0x5A)
			if k, ok := dynamicParams["xor_key"]; ok && len(k) > 0 {
				xorKey = k[0]
			}
			err = KineticXorEncrypt(inputPath, outputPath, xorKey) // XOR reversible!

		case "kinetic_byte_invert":
			err = KineticByteInvert(inputPath, outputPath)

		case "kinetic_checksum":
			checksum, csErr := KineticChecksum(inputPath)
			if csErr != nil {
				err = csErr
			} else {
				core.BroadcastUpdate(jobID, "PROCESSING", 90,
					fmt.Sprintf("Checksum: 0x%08X", checksum))
				err = nil
			}
		}

	// === DYNAMIC REGISTRY TOOLS (The New Standard) ===
	// Menangani 150+ tools dari cli_registry.json secara otomatis
	default:
		core.BroadcastUpdate(jobID, "PROCESSING", 15, fmt.Sprintf("Mempersiapkan template untuk '%s'...", toolID))

		// Tentukan output extension jika ada di query atau gunakan default template
		// services.ExecuteUniversalTool akan menangani mapping {input}, {output}, etc.
		_, err = services.ExecuteUniversalTool(toolID, inputPath, outputPath, cacheDir, dynamicParams)

		if err != nil && strings.Contains(err.Error(), "TOOL_NOT_FOUND") {
			// Fallback jika benar-benar tidak ada di registry
			err = fmt.Errorf("alat '%s' belum dikenal atau mesin belum terpasang", toolID)
		}
	}

	// SELESAI atau GAGAL — 📡 SIARAN FINAL
	if err != nil {
		Tracker.MarkFailed(jobID, err.Error())
		log.Printf("❌ [JOB FAILED] %s: %v", jobID, err)
		// 📡 SIARAN GAGAL
		core.BroadcastUpdate(jobID, "FAILED", 0, fmt.Sprintf("Pemrosesan gagal: %v", err))
		// 🔥 OMNI-DB: Catat kegagalan ke Firestore
		core.RecordJobFailed(jobID, err.Error())
	} else {
		Tracker.MarkDone(jobID, outputPath)
		log.Printf("✅ [JOB DONE] %s → %s", jobID, outputPath)
		// 📡 SIARAN SELESAI (download URL otomatis disisipkan oleh Broadcaster)
		core.BroadcastUpdate(jobID, "COMPLETED", 100, "Pemrosesan selesai! File siap diunduh.")
		// 🔥 OMNI-DB: Catat sukses ke Firestore
		core.RecordJobDone(jobID, outputPath)
	}
}

// isNativeVideoTool cek apakah alat menggunakan handler Go manual (seperti thumbnail)
func isNativeVideoTool(toolID string) bool {
	nativeVideo := map[string]bool{
		"video_thumbnail": true, "video_audio_extract": true,
	}
	return nativeVideo[toolID]
}

// IsKineticTool cek apakah alat menggunakan OMNI-KINETIC C Hyper-Engine
// Tools ini berjalan langsung di memori C — tanpa exec.Command!
func IsKineticTool(toolID string) bool {
	kineticTools := map[string]bool{
		"kinetic_xor_encrypt": true,
		"kinetic_xor_decrypt": true,
		"kinetic_byte_invert": true,
		"kinetic_checksum":    true,
	}
	return kineticTools[toolID]
}

// ==========================================
// ==========================================
// JOB STATUS HANDLER (Polling Endpoint)
// ==========================================

// JobStatusHandler mengembalikan status pekerjaan untuk polling dari browser
// GET /api/v1/job?id=JOB-xxx
func JobStatusHandler(w http.ResponseWriter, r *http.Request) {
	ctx := &core.OmniContext{W: w, R: r}

	jobID := r.URL.Query().Get("id")
	if jobID == "" {
		// Jika tidak ada ID, kembalikan semua pekerjaan (dashboard monitoring)
		allJobs := Tracker.GetAllJobs()
		ctx.JSON(200, true, "Daftar semua pekerjaan", allJobs)
		return
	}

	job, found := Tracker.GetJob(jobID)
	if !found {
		ctx.JSON(404, false, "Pekerjaan tidak ditemukan", nil)
		return
	}

	ctx.JSON(200, true, job.Message, job)
}

// ==========================================
// FILE DOWNLOAD HANDLER
// ==========================================

// DownloadHandler mengirim file hasil pemrosesan ke browser
// GET /api/v1/download?job_id=JOB-xxx
func DownloadHandler(w http.ResponseWriter, r *http.Request) {
	ctx := &core.OmniContext{W: w, R: r}

	jobID := r.URL.Query().Get("job_id")
	if jobID == "" {
		ctx.JSON(400, false, "job_id wajib dikirim", nil)
		return
	}

	job, found := Tracker.GetJob(jobID)
	if !found {
		ctx.JSON(404, false, "Pekerjaan tidak ditemukan", nil)
		return
	}

	if job.Status != "done" {
		ctx.JSON(400, false, "File belum siap. Status: "+job.Status, map[string]interface{}{
			"status":   job.Status,
			"progress": job.Progress,
		})
		return
	}

	if _, err := os.Stat(job.OutputFile); os.IsNotExist(err) {
		ctx.JSON(404, false, "File output sudah dihapus atau tidak ditemukan", nil)
		return
	}

	// Set header untuk download
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", filepath.Base(job.OutputFile)))
	w.Header().Set("Content-Type", "application/octet-stream")

	// Stream file ke browser (ServeFile mendukung Range request otomatis)
	http.ServeFile(w, r, job.OutputFile)
}

// ==========================================
// HELPER: Response JSON standar (internal engine)
// ==========================================
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
