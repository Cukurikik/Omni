package core

import (
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// ==========================================
// 📡 OMNI-RESONANCE: Jaringan Saraf Live-Reload
// ==========================================
// Sistem ini menjaga koneksi WebSocket tetap hidup antara
// Golang Gateway dan setiap tab browser yang terhubung.
// Ketika OMNI-SIGHT (file watcher) mendeteksi perubahan,
// sinyal RELOAD_SIGNAL dikirim ke semua klien secara simultan.
// ==========================================

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true }, // Izinkan semua koneksi lokal
}

// Hub menyimpan semua koneksi browser yang aktif
type ResonanceHub struct {
	mu      sync.Mutex
	clients map[*websocket.Conn]bool
}

var hub = &ResonanceHub{
	clients: make(map[*websocket.Conn]bool),
}

// addClient menambahkan koneksi baru ke hub
func (h *ResonanceHub) addClient(conn *websocket.Conn) {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.clients[conn] = true
}

// removeClient menghapus koneksi yang terputus dari hub
func (h *ResonanceHub) removeClient(conn *websocket.Conn) {
	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.clients, conn)
	conn.Close()
}

// broadcast mengirim pesan ke SEMUA browser yang terhubung
func (h *ResonanceHub) broadcast(message []byte) {
	h.mu.Lock()
	defer h.mu.Unlock()

	deadClients := []*websocket.Conn{}

	for conn := range h.clients {
		err := conn.WriteMessage(websocket.TextMessage, message)
		if err != nil {
			deadClients = append(deadClients, conn)
		}
	}

	// Bersihkan koneksi mati
	for _, dead := range deadClients {
		delete(h.clients, dead)
		dead.Close()
	}
}

// ResonanceHandler menjaga koneksi WebSocket tetap hidup dengan Browser.
// Route: /ws/omni_live
func ResonanceHandler(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("📡 [RESONANCE] Gagal upgrade WebSocket: %v", err)
		return
	}

	hub.addClient(conn)
	clientCount := len(hub.clients)
	log.Printf("📡 [RESONANCE] Browser terhubung ke Jaringan Saraf OMNI. Total klien: %d", clientCount)

	// Keep-alive loop: membaca pesan dari klien (untuk deteksi disconnect)
	defer hub.removeClient(conn)
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			log.Printf("📡 [RESONANCE] Browser terputus. Sisa klien: %d", len(hub.clients)-1)
			break
		}
	}
}

// TriggerReloadHandler menerima sinyal dari OMNI-SIGHT (file watcher)
// lalu meneruskannya ke semua browser yang terhubung.
// Route: /api/internal/trigger-reload
func TriggerReloadHandler(w http.ResponseWriter, r *http.Request) {
	clientCount := len(hub.clients)

	if clientCount == 0 {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok","message":"Tidak ada browser yang terhubung."}`))
		return
	}

	hub.broadcast([]byte("RELOAD_SIGNAL"))
	log.Printf("📡 [RESONANCE] Sinyal RELOAD dikirim ke %d browser.", clientCount)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"ok","message":"Sinyal reload berhasil dikirim."}`))
}
