package routes

import (
	"encoding/json"
	"net/http"

	"omnitools/core"
)

// ==========================================
// ⚡ OMNI-WASM: STATUS ENDPOINT
// ==========================================
// Route: GET /api/v1/wasm/status
// Mengembalikan status runtime Wasm dan daftar modul terdaftar.

func WasmStatusHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	response := map[string]interface{}{
		"enabled": core.IsWasmEnabled(),
		"status":  core.GetWasmStatus(),
		"modules": core.GetWasmModules(),
	}

	json.NewEncoder(w).Encode(response)
}
