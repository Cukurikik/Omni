package services

import (
	"fmt"
	"net/http"
	"sync"
	"time"
)

// Channel untuk mengirim pesan log ke UI secara real-time
var logChan = make(chan string, 100)
var clientsMutex sync.Mutex

// MonitorHandler mengirimkan data sistem secara streaming (SSE)
func MonitorHandler(w http.ResponseWriter, r *http.Request) {
	// Set header wajib SSE
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	// CORS ini penting jika UI berjalan di port terpisah (React/Vite port 3000)
	w.Header().Set("Access-Control-Allow-Origin", "http://localhost:3000")

	// Pipa pesan untuk client ini
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming tidak didukung!", http.StatusInternalServerError)
		return
	}

	// Jangan blok loop, biarkan loop ini hidup sampai browser ditutup
	for {
		select {
		case msg := <-logChan:
			// Kirim Log Live
			fmt.Fprintf(w, "event: log\ndata: %s\n\n", msg)
			flusher.Flush()
		case <-time.After(1 * time.Second):
			// Hitung total Kapasitas dan Antrean saat ini dari The Fair Manager
			totalWorkers := MaxFastWorkers + MaxMediumWorkers + MaxHeavyWorkers
			totalQueue := len(FastQueue) + len(MediumQueue) + len(HeavyQueue)

			stats := fmt.Sprintf(`{"active_workers": %d, "queue_len": %d, "timestamp": %d}`,
				totalWorkers, totalQueue, time.Now().Unix())
			fmt.Fprintf(w, "event: stats\ndata: %s\n\n", stats)
			flusher.Flush()
		case <-r.Context().Done():
			// Client menutup browser
			return
		}
	}
}

// BroadcastLog mengirim log ke stream SSE (Non-blocking)
func BroadcastLog(layer, code, msg string) {
	entry := fmt.Sprintf("[%s] %s: %s", layer, code, msg)
	select {
	case logChan <- entry:
	default: // Jika channel penuh, abaikan agar server tidak lag
	}
}
