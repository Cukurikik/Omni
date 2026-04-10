// ==========================================
// 🐍 OMNI-SYNAPSE: STUB (Non-CGO Fallback)
// ==========================================
// File ini aktif saat CGO TIDAK tersedia atau Python tag tidak aktif.
// Semua fungsi Synapse mengembalikan error "not available".
// ==========================================

//go:build !cgo || !python

package net

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

// ==========================================
// 🧠 SYNAPSE ENGINE STUB
// ==========================================

type SynapseEngine struct {
	initialized   bool
	fastapiLoaded bool
	startTime     time.Time
}

var (
	synapseInstance *SynapseEngine
)

func GetSynapse() *SynapseEngine {
	if synapseInstance == nil {
		synapseInstance = &SynapseEngine{
			startTime: time.Now(),
		}
	}
	return synapseInstance
}

func (s *SynapseEngine) IgniteFastAPI(modulePath, moduleName, appVar string) error {
	return fmt.Errorf("[OMNI-SYNAPSE] CGO/Python tidak tersedia. Build dengan: CGO_ENABLED=1 -tags 'cgo python'")
}

func (s *SynapseEngine) ExecuteFastAPICall(method, path, queryString, body string, headers map[string]string) (int, map[string]string, string, error) {
	return 503, nil, "", fmt.Errorf("[OMNI-SYNAPSE] FastAPI tidak tersedia (CGO disabled)")
}

func (s *SynapseEngine) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"initialized":    false,
		"fastapi_loaded": false,
		"mode":           "STUB_NO_CGO",
		"error":          "CGO/Python tidak tersedia",
	}
}

// HandlePythonRoute stub — returns service unavailable
func HandlePythonRoute(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusServiceUnavailable)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"error":   "OMNI-SYNAPSE tidak tersedia: CGO disabled",
		"hint":    "Build dengan: CGO_ENABLED=1 -tags 'cgo python'",
		"runtime": "OMNI-JS/1.5.0-SYNAPSE (STUB)",
	})
}

// SynapseHandleSyscall stub
func SynapseHandleSyscall(command string, argsJSON string) string {
	log.Printf("⚠️ [SYNAPSE-STUB] Syscall '%s' dipanggil tapi CGO disabled", command)
	errJSON, _ := json.Marshal(map[string]string{
		"error": fmt.Sprintf("OMNI-SYNAPSE tidak tersedia (CGO disabled). Command: %s", command),
	})
	return string(errJSON)
}
