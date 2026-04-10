package routes

import (
	"encoding/json"
	"net/http"
	"time"
)

// OMNI_ORACLE_MOCK_REGISTRY menyimpan daftar rute otomatis
var OracleMockRoutes = map[string]http.HandlerFunc{}

func init() {
	OracleMockRoutes["/api/v1/tools/universal/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "mocked",
			"message": "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint": "/api/v1/tools/universal/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
}
