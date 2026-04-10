package routes

import (
	"encoding/json"
	"net/http"

	"omnitools/core"
)

// ==========================================
// 🔌 OMNI-ADAPTER: Status API Handler
// ==========================================

// AdapterStatusHandler menampilkan status kesehatan semua third-party adapter.
// Route: GET /api/v1/adapters/status
//
// Response:
//
//	{
//	  "adapters": [
//	    { "name": "stripe", "state": "ACTIVE", "fail_count": 0 },
//	    { "name": "openai", "state": "DEGRADED", "fail_count": 2 }
//	  ],
//	  "total": 2
//	}
func AdapterStatusHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	adapters := core.CheckAllAdapters()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"adapters": adapters,
		"total":    len(adapters),
	})
}
