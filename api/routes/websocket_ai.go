package routes

import (
	"bufio"
	"fmt"
	"net/http"
	"os/exec"

	"github.com/gorilla/websocket"
	"omnitools/services"
)

// Upgrader: Konfigurasi Jembatan (Mengubah koneksi HTTP menjadi WebSocket konstan)
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	// Memperbolehkan Vite Dashboard JSX di localhost:5173 / localhost:3000 untuk menembus CORS
	CheckOrigin: func(r *http.Request) bool { return true },
}

// AiChatStreamHandler - Gerbang Real-Time penyambung Browser ke Python
func AiChatStreamHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Upgrade request menjadi jalur Pipa TCP dua-arah (WebSocket)
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		services.WriteLog("WEBSOCKET", "ERR_WS_UPGRADE", fmt.Sprintf("Gagal membuka koneksi AI: %v", err))
		return
	}
	defer conn.Close()

	services.WriteLog("WEBSOCKET", "INFO_WS_CONN", "Koneksi UI Terminal AI berhasil dibangun!")

	// 2. Loop penantian komunikasi
	for {
		// Tunggu kueri pesan (Prompt) dari JSX Frontend
		messageType, promptData, err := conn.ReadMessage()
		if err != nil {
			services.WriteLog("WEBSOCKET", "WARN_WS_CLOSE", "Koneksi terputus/ditutup oleh UI.")
			break
		}

		prompt := string(promptData)
		services.WriteLog("AI KOGNITIF", "INFO_PROMPT", fmt.Sprintf("Prompt Diterima: %s", prompt))

		// 3. Panggil Python secara Stateless.
		// NOTE: Path relatif merujuk dari eksekusi `api/main.go` ke direktori Python kita.
		cmd := exec.Command("python", "../scripts/ai_tools/chat_worker.py", prompt)

		// 4. Hubungkan Pipa Output Python (Stdout) langsung ke ingatan Golang
		stdout, err := cmd.StdoutPipe()
		if err != nil {
			services.WriteLog("WEBSOCKET", "ERR_PY_PIPE", fmt.Sprintf("Pipa Stdout Python Error: %v", err))
			conn.WriteMessage(messageType, []byte(`{"success": false, "message": "Gagal menghubungkan AI Engine"}`))
			continue
		}

		// Mulai rantai otak Python - Ia akan hidup saat ini juga
		if err := cmd.Start(); err != nil {
			services.WriteLog("WEBSOCKET", "ERR_PY_START", fmt.Sprintf("Gagal memulai engine Python: %v", err))
			conn.WriteMessage(messageType, []byte(`{"success": false, "message": "Python tidak dapat dijalankan."}`))
			continue
		}

		services.WriteLog("AI KOGNITIF", "INFO_PY_STREAM", "Python Stream dihidupkan, Memulai Scanning Output...")

		// 5. Baca Pipa output Python baris demi baris secara murni seketika.
		scanner := bufio.NewScanner(stdout)
		for scanner.Scan() {
			jsonChunk := scanner.Bytes()

			// 6. Semburkan Teks Llama/GPT ini ke React UI secara konstan!
			err = conn.WriteMessage(messageType, jsonChunk)
			if err != nil {
				services.WriteLog("WEBSOCKET", "ERR_WS_SEND", fmt.Sprintf("Gagal mengirim paket ke UI: %v", err))
				break
			}
		}

		// 7. Hancurkan Python secara paksa agar sisa "Amnesia Stateless Rule" ditegakkan.
		// Membebaskan seluruh bobot RAM (GBs) dari Python script model.
		cmd.Wait()
		services.WriteLog("WEBSOCKET", "INFO_PY_KILL", "Python dihentikan & memori dibersihkan.")
	}
}
