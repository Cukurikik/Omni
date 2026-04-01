package routes

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"omnitools/services"
)

// HotSwapHandler merespons `/api/v1/system/hotswap`.
// Melalui endpoint sakti ini, Engineer dapat menimpa Logic C++ secara instan
// Tanpa menghentikan Nginx atau Go-Server sekalipun!
func HotSwapHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Metode Alchemist Tertolak (Wajib POST)", http.StatusMethodNotAllowed)
		return
	}

	// Batas Payload (Engine V2 jarang melebihi 200 MB)
	r.ParseMultipartForm(200 << 20)

	binaryName := r.FormValue("binary_name") // misal: "ffmpeg" atau "omni_audio_core"
	if binaryName == "" {
		http.Error(w, "Target Mesin (binary_name) kosong!", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("engine_file")
	if err != nil {
		http.Error(w, "File Mesin Gagal Diambil", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 1. Simpan di Markas Alchemist dengan penanda waktu Absolut
	versionID := time.Now().Unix()
	newEngineFileName := fmt.Sprintf("%s_v%d", binaryName, versionID)
	// Kita menyimpan absolut di `../release/engines/`
	newAbsPath, _ := filepath.Abs(filepath.Join(services.EngineDir, newEngineFileName))

	// Pastikan markas ada
	if _, err := os.Stat(services.EngineDir); os.IsNotExist(err) {
		os.MkdirAll(services.EngineDir, os.ModePerm)
	}

	dst, err := os.Create(newAbsPath)
	if err != nil {
		http.Error(w, "Gagal menancapkan mesin ke server", http.StatusInternalServerError)
		return
	}

	// Karena Biner eksekusi ukurannya kecil (maksimal ratusan MB), RAM aman.
	io.Copy(dst, file)
	dst.Close()

	// 2. Wajib memberikan Hak Akses Eksekusi (Chmod +x) supaya OS Kernel bisa memanggilnya
	os.Chmod(newAbsPath, 0755)

	// 3. ATOMIC SWAP SYMLINK (Zero-Downtime)
	errSwap := services.SwapBinaryEngine(binaryName, newAbsPath)
	if errSwap != nil {
		services.WriteLog("ALCHEMIST", "ERROR", fmt.Sprintf("Gagal Swap Mesin %s -> %v", binaryName, errSwap))
		http.Error(w, "Kegagalan Fatal dalam penukaran Symlink Inode!", http.StatusInternalServerError)
		return
	}

	// Sukses Mutlak!
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"layer":   "SYSTEM_ALCHEMIST",
		"code":    "OK_ZERO_DOWNTIME_SWAP",
		"message": fmt.Sprintf("Mesin [%s] resmi digantikan oleh versi (%d). Pekerjaan berjalan tidak terpotong!", binaryName, versionID),
	})
}
