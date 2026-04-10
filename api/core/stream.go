package core

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

// ==========================================
// 📡 OMNI-STREAM: SSE (Server-Sent Events) ENGINE
// ==========================================
// Menggantikan WebSocket untuk skenario satu-arah (server → browser):
// - Job progress monitoring
// - System event notifications
// - Real-time dashboard updates
//
// Mengapa SSE lebih unggul dari WebSocket untuk kasus ini?
//   1. HEMAT BATERAI: Tidak ada ping/pong frame yang menguras baterai mobile
//   2. AUTO-RECONNECT: Browser otomatis menyambung ulang tanpa kode tambahan
//   3. HTTP/2 MULTIPLEXING: Satu koneksi TCP untuk banyak stream
//   4. CACHE-FRIENDLY: Kompatibel dengan CDN dan reverse proxy
//   5. SEDERHANA: Tidak butuh library gorilla/websocket — HTTP murni!
//
// Perhatian: OMNI tetap mempertahankan WebSocket untuk kasus dua-arah
// (AI Chat, WebRTC Signaling). SSE hanya untuk broadcast satu-arah.
//
// Frontend cukup:
//   const es = new EventSource("/api/v1/stream/jobs?job_id=JOB-123");
//   es.onmessage = (e) => { const data = JSON.parse(e.data); ... };
// ==========================================

// StreamPayload adalah format data yang dikirim via SSE
type StreamPayload struct {
	JobID       string `json:"job_id"`
	Status      string `json:"status"`       // QUEUED | PROCESSING | COMPLETED | FAILED
	Progress    int    `json:"progress"`      // 0-100
	Message     string `json:"message"`
	DownloadURL string `json:"download_url,omitempty"`
	Timestamp   int64  `json:"timestamp"`
}

// ==========================================
// MENARA SSE: Channel-Based Stream Hub
// ==========================================

type sseHub struct {
	mu      sync.RWMutex
	streams map[string][]chan StreamPayload // jobID → daftar SSE channels
}

var streamHub = &sseHub{
	streams: make(map[string][]chan StreamPayload),
}

// ==========================================
// ENDPOINT: GET /api/v1/stream/jobs?job_id=JOB-xxx
// ==========================================
// Browser membuka koneksi SSE. Server mengirim event setiap ada update.
// Koneksi otomatis ditutup saat job COMPLETED/FAILED.

// SSEJobStreamHandler menangani koneksi SSE untuk monitoring job real-time.
// Route: /api/v1/stream/jobs (didaftarkan di router.go)
func SSEJobStreamHandler(w http.ResponseWriter, r *http.Request) {
	jobID := r.URL.Query().Get("job_id")
	if jobID == "" {
		http.Error(w, `{"error":"job_id wajib dikirim"}`, http.StatusBadRequest)
		return
	}

	// Pastikan ResponseWriter mendukung Flusher (wajib untuk SSE)
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, `{"error":"streaming tidak didukung oleh server ini"}`, http.StatusInternalServerError)
		return
	}

	// Set SSE headers
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no") // Matikan buffering Nginx
	w.Header().Set("Access-Control-Allow-Origin", "*")

	// Buat channel unik untuk client ini
	ch := make(chan StreamPayload, 10) // Buffer 10 event

	// Daftarkan channel ke hub
	streamHub.mu.Lock()
	streamHub.streams[jobID] = append(streamHub.streams[jobID], ch)
	listenerCount := len(streamHub.streams[jobID])
	streamHub.mu.Unlock()

	log.Printf("📡 [OMNI-STREAM] SSE client terhubung: Job %s (total listeners: %d)", jobID, listenerCount)

	// Kirim initial event (confirm connected)
	initialPayload := StreamPayload{
		JobID:     jobID,
		Status:    "CONNECTED",
		Progress:  0,
		Message:   "SSE stream aktif. Menunggu update...",
		Timestamp: time.Now().Unix(),
	}
	writeSSEEvent(w, flusher, initialPayload)

	// Cleanup saat client disconnect
	ctx := r.Context()

	defer func() {
		streamHub.removeStream(jobID, ch)
		close(ch)
		log.Printf("📡 [OMNI-STREAM] SSE client terputus: Job %s", jobID)
	}()

	// Event loop: kirim data saat ada update
	for {
		select {
		case <-ctx.Done():
			// Client disconnect (browser ditutup, halaman diganti)
			return

		case payload, ok := <-ch:
			if !ok {
				return // Channel ditutup
			}

			writeSSEEvent(w, flusher, payload)

			// Auto-close setelah job selesai/gagal
			if payload.Status == "COMPLETED" || payload.Status == "FAILED" {
				return
			}
		}
	}
}

// writeSSEEvent menulis satu event SSE ke ResponseWriter
func writeSSEEvent(w http.ResponseWriter, flusher http.Flusher, payload StreamPayload) {
	data, err := json.Marshal(payload)
	if err != nil {
		return
	}

	// Format SSE: "data: {json}\n\n"
	fmt.Fprintf(w, "data: %s\n\n", data)
	flusher.Flush()
}

// removeStream menghapus satu channel dari daftar listener sebuah job
func (h *sseHub) removeStream(jobID string, ch chan StreamPayload) {
	h.mu.Lock()
	defer h.mu.Unlock()

	channels := h.streams[jobID]
	for i, c := range channels {
		if c == ch {
			h.streams[jobID] = append(channels[:i], channels[i+1:]...)
			break
		}
	}

	if len(h.streams[jobID]) == 0 {
		delete(h.streams, jobID)
	}
}

// ==========================================
// FUNGSI PENYIARAN SSE: Dipanggil oleh Worker Pool / Engine
// ==========================================

// StreamUpdate menyiarkan update progres via SSE ke SEMUA browser yang memantau jobID.
// Ini adalah fungsi publik utama — pengganti BroadcastUpdate untuk koneksi SSE.
//
// Contoh:
//
//	core.StreamUpdate("JOB-123", "PROCESSING", 50, "Mengekstrak frame video...")
//	core.StreamUpdate("JOB-123", "COMPLETED", 100, "Selesai!")
func StreamUpdate(jobID string, status string, progress int, message string) {
	streamHub.mu.RLock()
	channels, exists := streamHub.streams[jobID]
	streamHub.mu.RUnlock()

	if !exists || len(channels) == 0 {
		return // Tidak ada SSE listener — skip
	}

	payload := StreamPayload{
		JobID:     jobID,
		Status:    status,
		Progress:  progress,
		Message:   message,
		Timestamp: time.Now().Unix(),
	}

	if status == "COMPLETED" {
		payload.DownloadURL = "/api/v1/download/result?job_id=" + jobID
	}

	// Kirim ke SEMUA SSE listeners (non-blocking)
	streamHub.mu.RLock()
	for _, ch := range channels {
		select {
		case ch <- payload:
		default:
			// Channel penuh — skip (client lambat)
		}
	}
	streamHub.mu.RUnlock()

	// Log hanya untuk status penting (bukan setiap progress tick)
	if status == "COMPLETED" || status == "FAILED" || progress%25 == 0 {
		log.Printf("📡 [OMNI-STREAM] Broadcast SSE → Job %s | %s | %d%%", jobID, status, progress)
	}
}

// BroadcastAndStream mengirim update sekaligus ke WebSocket DAN SSE.
// Ini memungkinkan transisi bertahap: client lama masih pakai WebSocket,
// client baru pakai SSE. Keduanya menerima update yang sama.
func BroadcastAndStream(jobID string, status string, progress int, message string) {
	// WebSocket (legacy — untuk backward compatibility)
	BroadcastUpdate(jobID, status, progress, message)

	// SSE (modern — hemat baterai)
	StreamUpdate(jobID, status, progress, message)
}

// GetActiveSSEListeners mengembalikan jumlah job yang dipantau via SSE
func GetActiveSSEListeners() int {
	streamHub.mu.RLock()
	defer streamHub.mu.RUnlock()
	return len(streamHub.streams)
}
