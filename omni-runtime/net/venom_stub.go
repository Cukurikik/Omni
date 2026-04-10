// ==========================================
// 🛡️ OMNI-VENOM: STUB (No-Python Fallback)
// ==========================================
// File ini aktif pada SEMUA build NORMAL (tanpa tag 'python').
// Ini memastikan kode tetap bisa di-compile tanpa Python headers.
//
// Developer yang tidak butuh Python tetap bisa build OMNI tanpa error.
// Jika mereka memanggil syscall 'venom_execute', mereka akan mendapat
// pesan jelas bahwa Python belum diaktifkan.
//
// Untuk mengaktifkan mode PENUH:
//   1. Install Python 3.10+ dengan dev headers
//   2. Build dengan: go build -tags "python" ./cmd/
// ==========================================

//go:build !cgo || !python

package net

import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
)

// ==========================================
// 🐍 VENOM STUB ENGINE
// ==========================================

const venomStubWarning = "⚠️ [OMNI-VENOM] Python TIDAK AKTIF — Build tanpa tag 'python' atau CGO disabled"

type VenomEngine struct {
	mu          sync.Mutex
	initialized bool
	scriptsDir  string
}

var (
	venomInstance *VenomEngine
	venomOnce    sync.Once
)

func init() {
	log.Println(venomStubWarning)
}

// GetVenom returns stub VenomEngine
func GetVenom() *VenomEngine {
	venomOnce.Do(func() {
		venomInstance = &VenomEngine{
			scriptsDir: "./venom_scripts",
		}
	})
	return venomInstance
}

// IgnitePythonMatrix stub — tidak melakukan apa-apa
func (v *VenomEngine) IgnitePythonMatrix() error {
	log.Println(venomStubWarning)
	return fmt.Errorf("OMNI-VENOM: Python tidak tersedia (build tanpa tag 'python')")
}

// ExecutePythonScript stub
func (v *VenomEngine) ExecutePythonScript(scriptName, functionName, jsonArgs string) (string, error) {
	return "", fmt.Errorf("OMNI-VENOM: Python tidak aktif. Build dengan: go build -tags python ./cmd/")
}

// ExecuteRawPython stub
func (v *VenomEngine) ExecuteRawPython(code string) (string, error) {
	return "", fmt.Errorf("OMNI-VENOM: Python tidak aktif. Build dengan: go build -tags python ./cmd/")
}

// GetVenomStatus stub
func (v *VenomEngine) GetVenomStatus() map[string]interface{} {
	return map[string]interface{}{
		"initialized":    false,
		"python_version": "STUB-MODE (Python tidak tersedia)",
		"scripts_dir":    v.scriptsDir,
		"mode":           "STUB",
		"bridge":         "NO_PYTHON",
		"activate_hint":  "go build -tags python ./cmd/",
	}
}

// ShutdownPython stub
func (v *VenomEngine) ShutdownPython() {
	// No-op
}

// VenomHandleSyscall stub — mengembalikan error terstruktur untuk semua command
func VenomHandleSyscall(command string, argsJSON string) string {
	switch command {
	case "venom_execute":
		// Stub: generate mock response berdasarkan function name
		var args map[string]interface{}
		json.Unmarshal([]byte(argsJSON), &args)

		script, _ := args["script"].(string)
		funcName, _ := args["func"].(string)

		log.Printf("🐍 [VENOM-STUB] Menerima permintaan %s.%s() — Mode Stub aktif", script, funcName)

		// Berikan template response yang bermakna
		stubResult := map[string]interface{}{
			"result": fmt.Sprintf("[STUB] %s.%s() → Python tidak aktif. "+
				"Build dengan: go build -tags python ./cmd/", script, funcName),
			"mode":    "stub",
			"script":  script,
			"func":    funcName,
		}
		resultJSON, _ := json.Marshal(stubResult)
		return string(resultJSON)

	case "venom_raw":
		var args map[string]interface{}
		json.Unmarshal([]byte(argsJSON), &args)
		code, _ := args["code"].(string)

		log.Printf("🐍 [VENOM-STUB] Raw Python request (code length: %d) — Mode Stub aktif", len(code))

		stubResult := map[string]interface{}{
			"output": "[STUB] Raw Python tidak tersedia. Build dengan tag 'python'.",
			"mode":   "stub",
		}
		resultJSON, _ := json.Marshal(stubResult)
		return string(resultJSON)

	case "venom_status":
		status := GetVenom().GetVenomStatus()
		statusJSON, _ := json.Marshal(status)
		return string(statusJSON)

	case "venom_ignite":
		errJSON, _ := json.Marshal(map[string]interface{}{
			"error":  "Python tidak tersedia (build tanpa tag 'python')",
			"status": "PYTHON_OFFLINE",
			"hint":   "go build -tags python ./cmd/",
		})
		return string(errJSON)

	default:
		errJSON, _ := json.Marshal(map[string]string{
			"error": fmt.Sprintf("Venom command tidak dikenal: %s", command),
		})
		return string(errJSON)
	}
}
