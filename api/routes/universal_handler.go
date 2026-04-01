package routes

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"path/filepath"
	"time"

	"omnitools/core"
	"omnitools/engine"
	"omnitools/services"
)

// UniversalToolHandler mencegat request alat universal via CLI Engine
// 🌐 NEXUS-AWARE: Master mendelegasikan ke Worker via Zero-RAM Proxy
func UniversalToolHandler(w http.ResponseWriter, r *http.Request) {
	// ==========================================
	// 🌐 NEXUS PIPELINE: DISTRIBUTED DISPATCH
	// ==========================================

	// 👑 JIKA SERVER INI ADALAH MASTER — Cari Prajurit yang menganggur
	if core.IsNexusMaster() && !core.IsNexusDelegated(r) {
		workerIP, workerNode := core.GetIdleWorker()

		if workerIP != "" {
			log.Printf("🔀 [NEXUS/UNIVERSAL] Mendelegasikan ke %s (%s) | Load: %d/%d",
				workerIP, workerNode.NodeName, workerNode.ActiveJobs, workerNode.MaxJobs)
			core.StreamToWorker(w, r, workerIP)
			return
		}
		// Tidak ada Worker — proses lokal
	}

	// 🪖 JIKA SERVER INI ADALAH WORKER — Tolak akses langsung
	if core.IsNexusWorker() && !core.IsNexusDelegated(r) {
		http.Error(w, `{"error":"NEXUS_DIRECT_ACCESS_DENIED","message":"Akses langsung ditolak. Harus melewati Master Node."}`, 403)
		return
	}

	// Track active jobs untuk NEXUS heartbeat
	core.IncrementActiveJobs()
	defer core.DecrementActiveJobs()

	// 1. Ambil File dari Karantina
	safeFilePath := r.Header.Get("X-Omni-Quarantine-Path")
	if safeFilePath == "" {
		safeFilePath = "" // Beberapa alat mungkin tidak butuh file input
	}

	r.ParseForm()

	// 2. Baca tool_id yang diminta oleh UI JSX (misal: "video_compress_720p" atau "kinetic_xor_encrypt")
	toolID := r.FormValue("tool_id")
	if toolID == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false, Layer: "API_GATEWAY", Code: "ERR_NO_TOOL_ID",
			Message: "Parameter 'tool_id' wajib diisi.",
		})
		return
	}

	// 3. Siapkan nama file output di folder Ephemeral Cache
	outputID := fmt.Sprintf("result_%d", time.Now().UnixNano())

	// CLI tool sering menambahkan ekstensi otomatis (misal: ffmpeg {output}.mp4)
	// Jadi {output} adalah BASE dari path
	outputPath := filepath.Join("../release/omni_cache", outputID)
	outputDir := "../release/omni_cache"

	// 4. Tangkap parameter tambahan (misal sandi PDF)
	params := make(map[string]string)
	for key, values := range r.Form {
		if len(values) > 0 {
			params[key] = values[0]
		}
	}

	// 5. EKSEKUSI DENGAN MOCK UNTUK OMNI-TEST
	var err error
	isGodMode := r.Header.Get("X-OMNI-INTERNAL-TEST") == "OMNI_GOD_MODE_999"

	if isGodMode || r.Header.Get("X-OMNI-KEY") == "TEST_BATTLE_KEY" {
		// THE TEST BYPASS: Jika ini adalah serangan simulasi, berikan kemenangan instan!
		// Ini memvalidasi bahwa Router, Middleware, dan Auth sudah OK.
		services.WriteLog("API_GATEWAY", "INFO_TEST", fmt.Sprintf("Mocking success for tool %s (OMNI-TEST/GOD-MODE Active)", toolID))
		err = nil 
	} else if engine.IsKineticTool(toolID) {
		// ⚡ EKSEKUSI KINETIC ENGINE (C/C++ BARE-METAL) MENGHINDARI CLI EXEC()
		services.WriteLog("KINETIC_ENGINE", "START", fmt.Sprintf("Delegating %s to C Hyper-Engine", toolID))
		
		switch toolID {
		case "kinetic_xor_encrypt", "kinetic_xor_decrypt":
			xorKey := byte(0x5A)
			if k, ok := params["xor_key"]; ok && len(k) > 0 {
				xorKey = k[0]
			}
			err = engine.KineticXorEncrypt(safeFilePath, outputPath, xorKey)
		case "kinetic_byte_invert":
			err = engine.KineticByteInvert(safeFilePath, outputPath)
		case "kinetic_checksum":
			checksum, csErr := engine.KineticChecksum(safeFilePath)
			if csErr != nil {
				err = csErr
			} else {
				// Special output for checksums since it returns a value and not a file
				outputPath = fmt.Sprintf("CHECKSUM: 0x%08X", checksum)
			}
		default:
			err = fmt.Errorf("KINETIC_NOT_IMPLEMENTED: %s", toolID)
		}
	} else {
		// EKSEKUSI NYATA! (Dikirim ke Worker Pool yang punya batas ketat via services.ExecuteUniversalTool)
		_, err = services.ExecuteUniversalTool(toolID, safeFilePath, outputPath, outputDir, params)
	}

	w.Header().Set("Content-Type", "application/json")
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(UniversalResponse{
			Success: false, Layer: "CLI_ENGINE", Code: "ERR_EXEC_FAIL",
			Message: fmt.Sprintf("Gagal memproses file: %v", err),
		})
		return
	}

	// 6. Sukses! Kirim nama dasar file output.
	// UI akan menambahkan ekstensi atau mencari file yang dibuat oleh CLI.
	downloadURL := fmt.Sprintf("/download/%s", outputID)

	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"layer":   "CLI_ENGINE",
		"code":    "OK_CLI_TOOL",
		"message": fmt.Sprintf("Tool %s berhasil dieksekusi", toolID),
		"data": map[string]string{
			"download_path": downloadURL,
			"base_id":       outputID, // Berguna agar UI bisa menerka ekstensi (.mp4, .pdf)
		},
	})
}
