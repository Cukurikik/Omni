package routes

import (
	"encoding/json"
	"fmt"
	"net/http"

	"omnitools/services"
)

// UniversalResponse — Kontrak JSON standar OMNI TOOLS untuk seluruh respons API
type UniversalResponse struct {
	Success   bool        `json:"success"`
	Layer     string      `json:"layer"`
	Code      string      `json:"code,omitempty"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
	Timestamp string      `json:"timestamp,omitempty"`
}

// ==========================================
// AUDIO HANDLER: Deteksi Drop EDM
// ==========================================
// Handler ini menerima file yang sudah melewati FileQuarantineHandler.
// Ia membaca path file dari internal header, lalu MENYERAHKAN tugas
// ke Pabrik Pekerja (Worker Pool) melalui services.SubmitJob().
func AudioDropHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Dapatkan path file yang sudah aman dari Middleware Karantina
	safeFilePath := r.Header.Get("X-Omni-Quarantine-Path")
	if safeFilePath == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false,
			Layer:   "SECURITY_GATEWAY",
			Code:    "ERR_NO_SANDBOX",
			Message: "Melewati tembok pertahanan!",
		})
		return
	}

	// 2. Serahkan ke Pabrik Pekerja!
	// Daripada memanggil C++ langsung, kita masukkan ke antrean.
	// Pekerja yang tersedia akan mengeksekusinya dengan Pisau Guillotine.
	args := []string{"analyze_edm_drop", safeFilePath}
	jobResult := services.SubmitJob("audio_detect_drop", "../release/engine_bin/omni_engine", args)

	w.Header().Set("Content-Type", "application/json")

	// 3. Evaluasi Hasil dari Pekerja
	if !jobResult.Success {
		// Antrean penuh ATAU C++ error/timeout
		w.WriteHeader(http.StatusServiceUnavailable) // HTTP 503
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false,
			Layer:   "API_GATEWAY",
			Code:    "ERR_ENGINE_UNAVAILABLE",
			Message: fmt.Sprintf("Engine gagal memproses: %v", jobResult.Error),
		})
		return
	}

	// 4. Jika sukses, kirim JSON mentah dari C++ langsung ke Frontend JSX
	// (C++ sudah mencetak dalam format JSON Universal, jadi kita teruskan apa adanya)
	w.Write(jobResult.Data)
}
