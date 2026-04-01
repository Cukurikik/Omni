package core

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// ==========================================
// 📡 OMNI-BROADCASTER: Jembatan Telepatis Worker → Browser
// ==========================================
// Sistem ini memungkinkan pekerja latar belakang (Worker Pool) untuk
// menyiarkan progres real-time langsung ke layar pengguna via WebSocket.
//
// Alur:
// 1. Browser buka ws://host/ws/jobs?job_id=JOB-xxx
// 2. Golang simpan koneksi di map[jobID]*wsConn
// 3. Worker memanggil BroadcastUpdate(jobID, "PROCESSING", 50, "...")
// 4. Browser terima JSON: { status, progress, message }
// 5. Selesai/Gagal → koneksi auto-putus (hemat RAM)
//
// Developer React cukup panggil: useOmniJob(jobId)
// ==========================================

// BroadcastPayload adalah pesan yang dikirim ke browser via WebSocket
type BroadcastPayload struct {
	JobID       string `json:"job_id"`
	Status      string `json:"status"`                 // QUEUED | PROCESSING | COMPLETED | FAILED
	Progress    int    `json:"progress"`               // 0-100
	Message     string `json:"message"`                // Pesan deskriptif atau download URL
	DownloadURL string `json:"download_url,omitempty"` // Hanya diisi saat COMPLETED
}

// ==========================================
// MENARA RADIO: Menyimpan Koneksi per Job ID
// ==========================================
// Satu Job bisa dipantau oleh beberapa browser (multi-tab/multi-device)

type broadcastHub struct {
	mu      sync.RWMutex
	clients map[string][]*websocket.Conn // jobID → daftar koneksi
}

var broadcaster = &broadcastHub{
	clients: make(map[string][]*websocket.Conn),
}

// upgrader untuk Broadcaster (terpisah dari Resonance untuk isolasi)
var broadcasterUpgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

// ==========================================
// ENDPOINT: ws://host/ws/jobs?job_id=JOB-xxx
// ==========================================

// JobStreamHandler adalah WebSocket endpoint untuk memantau progres job real-time.
// Route: /ws/jobs (didaftarkan di router.go)
func JobStreamHandler(w http.ResponseWriter, r *http.Request) {
	jobID := r.URL.Query().Get("job_id")
	if jobID == "" {
		http.Error(w, "job_id wajib dikirim", http.StatusBadRequest)
		return
	}

	// Upgrade HTTP → WebSocket
	conn, err := broadcasterUpgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("📡 [BROADCASTER] Gagal upgrade WebSocket: %v", err)
		return
	}

	// Daftarkan koneksi ke menara radio
	broadcaster.mu.Lock()
	broadcaster.clients[jobID] = append(broadcaster.clients[jobID], conn)
	clientCount := len(broadcaster.clients[jobID])
	broadcaster.mu.Unlock()

	log.Printf("📡 [BROADCASTER] Browser terhubung: Job %s (total listeners: %d)", jobID, clientCount)

	// Keep-alive loop: baca pesan dari klien (untuk deteksi disconnect)
	defer func() {
		broadcaster.removeClient(jobID, conn)
		conn.Close()
	}()

	for {
		if _, _, err := conn.ReadMessage(); err != nil {
			log.Printf("📡 [BROADCASTER] Browser terputus dari Job %s", jobID)
			break
		}
	}
}

// removeClient menghapus satu koneksi tertentu dari daftar listener sebuah job
func (h *broadcastHub) removeClient(jobID string, conn *websocket.Conn) {
	h.mu.Lock()
	defer h.mu.Unlock()

	conns := h.clients[jobID]
	for i, c := range conns {
		if c == conn {
			// Hapus element tanpa mengubah urutan
			h.clients[jobID] = append(conns[:i], conns[i+1:]...)
			break
		}
	}

	// Jika tidak ada listener lagi, bersihkan entry dari map
	if len(h.clients[jobID]) == 0 {
		delete(h.clients, jobID)
	}
}

// ==========================================
// FUNGSI PENYIARAN: Dipanggil oleh Worker Pool / Engine
// ==========================================

// BroadcastUpdate menyiarkan update progres ke SEMUA browser yang memantau jobID tertentu.
// Ini adalah fungsi publik utama yang dipanggil dari engine/handlers.go
//
// Contoh:
//
//	core.BroadcastUpdate("JOB-123", "PROCESSING", 50, "Mengekstrak frame video...")
//	core.BroadcastUpdate("JOB-123", "COMPLETED", 100, "/api/v1/download/result?job_id=JOB-123")
func BroadcastUpdate(jobID string, status string, progress int, message string) {
	broadcaster.mu.RLock()
	conns, exists := broadcaster.clients[jobID]
	broadcaster.mu.RUnlock()

	if !exists || len(conns) == 0 {
		// Tidak ada browser yang memantau job ini — skip (hemat CPU)
		return
	}

	payload := BroadcastPayload{
		JobID:    jobID,
		Status:   status,
		Progress: progress,
		Message:  message,
	}

	// Tambahkan download URL jika selesai
	if status == "COMPLETED" {
		payload.DownloadURL = "/api/v1/download/result?job_id=" + jobID
	}

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		log.Printf("📡 [BROADCASTER] Gagal marshal payload: %v", err)
		return
	}

	// Kirim ke SEMUA listener (multi-tab / multi-device)
	var deadConns []*websocket.Conn

	broadcaster.mu.RLock()
	for _, conn := range conns {
		err := conn.WriteMessage(websocket.TextMessage, payloadBytes)
		if err != nil {
			deadConns = append(deadConns, conn)
		}
	}
	broadcaster.mu.RUnlock()

	// Bersihkan koneksi mati
	for _, dead := range deadConns {
		broadcaster.removeClient(jobID, dead)
		dead.Close()
	}

	// Jika job selesai/gagal, putuskan semua koneksi untuk menghemat RAM
	if status == "COMPLETED" || status == "FAILED" {
		broadcaster.mu.Lock()
		if remaining, ok := broadcaster.clients[jobID]; ok {
			for _, conn := range remaining {
				// Kirim pesan terakhir lalu tutup
				conn.Close()
			}
			delete(broadcaster.clients, jobID)
		}
		broadcaster.mu.Unlock()

		log.Printf("📡 [BROADCASTER] Job %s %s — semua koneksi diputus.", jobID, status)
	}
}

// GetActiveListeners mengembalikan jumlah job yang sedang dipantau (untuk monitoring)
func GetActiveListeners() int {
	broadcaster.mu.RLock()
	defer broadcaster.mu.RUnlock()
	return len(broadcaster.clients)
}
