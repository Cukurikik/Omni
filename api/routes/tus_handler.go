package routes

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"omnitools/middleware"
	"omnitools/services"
)

// ==========================================
// THE UNSTOPPABLE: TUS ROUTER (File 50GB)
// ==========================================
// Endpoint mandiri yang mengimplementasikan sebagian protokol TUS.
// Digunakan khusus untuk mengawal unggahan Monster (Video Raksasa).

func TusHandler(w http.ResponseWriter, r *http.Request) {
	// 1. SET HEADER WAJIB PROTOKOL TUS (CORS Tembus Sabuk Keselamatan)
	w.Header().Set("Tus-Resumable", "1.0.0")
	w.Header().Set("Access-Control-Expose-Headers", "Tus-Resumable, Upload-Offset, Location, Upload-Length")
	w.Header().Set("Access-Control-Allow-Headers", "Tus-Resumable, Upload-Length, Upload-Offset, Content-Type, Upload-Metadata")
	w.Header().Set("Access-Control-Allow-Methods", "POST, HEAD, PATCH, OPTIONS")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	// 2. FASE MEMBANGUN FONDASI (POST)
	if r.Method == "POST" {
		lengthStr := r.Header.Get("Upload-Length")
		if lengthStr == "" {
			http.Error(w, "Header 'Upload-Length' pingsan", http.StatusBadRequest)
			return
		}

		// Ciptakan ID unik (Anti-Tabrakan)
		hashInput := fmt.Sprintf("tus-%d", time.Now().UnixNano())
		hash := sha256.Sum256([]byte(hashInput))
		safeFileName := hex.EncodeToString(hash[:]) // Sengaja tanpa ekstensi, ekstensi diatur nanti di UI Tool Caller
		safeFilePath := filepath.Join(middleware.QuarantineDir, safeFileName)

		f, err := os.Create(safeFilePath)
		if err != nil {
			http.Error(w, "Gagal membuat ruang fondasi di Karantina", http.StatusInternalServerError)
			return
		}
		f.Close()

		// Tandai ukuran akhir file ke dalam catatan pendamping '.info'
		os.WriteFile(safeFilePath+".info", []byte(lengthStr), 0644)

		services.WriteLog("TUS", "INFO_BORN", fmt.Sprintf("Wadah Baja TUS Lahir: %s (Kapasitas: %s bytes)", safeFileName, lengthStr))

		scheme := "http"
		if r.TLS != nil {
			scheme = "https"
		}
		// Location kembalian: /api/v1/tus/{id}
		location := fmt.Sprintf("%s://%s/api/v1/tus/%s", scheme, r.Host, safeFileName)

		w.Header().Set("Location", location)
		w.WriteHeader(http.StatusCreated)
		return
	}

	// Menangkap ID dari Path /api/v1/tus/{id}
	pathParts := strings.Split(r.URL.Path, "/")
	if len(pathParts) < 5 { // [ "", "api", "v1", "tus", "ID" ]
		http.Error(w, "ID TUS Tidak Terdeteksi", http.StatusBadRequest)
		return
	}
	fileID := pathParts[4]
	if fileID == "" {
		http.Error(w, "ID TUS Kosong", http.StatusBadRequest)
		return
	}

	safeFilePath := filepath.Join(middleware.QuarantineDir, fileID)

	info, err := os.Stat(safeFilePath)
	if os.IsNotExist(err) {
		http.Error(w, "Bangkai TUS tidak ditemukan di Karantina", http.StatusNotFound)
		return
	}

	// 3. FASE CEK LUKA (HEAD - RESUME)
	// Memberitahu Browser berapa sisa partikel byte yang harus dikirim jika internet putus.
	if r.Method == "HEAD" {
		w.Header().Set("Upload-Offset", strconv.FormatInt(info.Size(), 10))
		w.WriteHeader(http.StatusOK)
		return
	}

	// 4. FASE PENEBALAN DINDING (PATCH - CHUNKING MURNI TANPA RAM)
	if r.Method == "PATCH" {
		offsetStr := r.Header.Get("Upload-Offset")
		if offsetStr == "" {
			http.Error(w, "Bypass Ditolak! Upload-Offset kosong", http.StatusBadRequest)
			return
		}

		offset, _ := strconv.ParseInt(offsetStr, 10, 64)
		if info.Size() != offset {
			http.Error(w, fmt.Sprintf("Offset Tidak Cocok. File Asli: %d, Potongan Browser: %d", info.Size(), offset), http.StatusConflict)
			return
		}

		f, err := os.OpenFile(safeFilePath, os.O_WRONLY|os.O_APPEND, 0644)
		if err != nil {
			http.Error(w, "Gagal membuka File TUS dari disk", http.StatusInternalServerError)
			return
		}
		defer f.Close()

		// TEKNIK KUNCI ZERO-RAM: Pipeline Stream Mentahan 128KB!
		buffer := make([]byte, 128*1024)
		written, err := io.CopyBuffer(f, r.Body, buffer)
		if err != nil && err != io.EOF {
			services.WriteLog("TUS", "ERR_WRITE", fmt.Sprintf("Internet BROWSER PUTUS saat Patch TUS %s: %v", fileID, err))
		}

		newOffset := offset + written
		w.Header().Set("Upload-Offset", strconv.FormatInt(newOffset, 10))
		w.WriteHeader(http.StatusNoContent)

		services.WriteLog("TUS", "INFO_CHUNK_IN", fmt.Sprintf("TUS Menerima Potongan: %d bytes (Total: %d bytes di Karantina)", written, newOffset))

		// Opsional: Cek apakah offset == Upload-Length di *.info
		// Jika sama, hapus info, dan trigger handler selanjutnya jika Anda ingin.
		return
	}

	http.Error(w, "TUS Method Terdampar (Method Not Allowed)", http.StatusMethodNotAllowed)
}
