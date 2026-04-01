package routes

import (
	"encoding/json"
	"net/http"
	"time"
)

// OMNI_ORACLE_MOCK_REGISTRY menyimpan daftar rute otomatis
var OracleMockRoutes = map[string]http.HandlerFunc{}

func init() {
	OracleMockRoutes["/api/v1/tools/video/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "mocked",
			"message":   "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint":  "/api/v1/tools/video/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
	OracleMockRoutes["/api/v1/tools/audio/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "mocked",
			"message":   "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint":  "/api/v1/tools/audio/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
	OracleMockRoutes["/api/v1/tools/image/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "mocked",
			"message":   "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint":  "/api/v1/tools/image/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
	OracleMockRoutes["/api/v1/tools/pdf/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "mocked",
			"message":   "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint":  "/api/v1/tools/pdf/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
	OracleMockRoutes["/api/v1/tools/converter/execute"] = func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "mocked",
			"message":   "Ghost Handler Activated by OMNI-ORACLE",
			"endpoint":  "/api/v1/tools/converter/execute",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	}
}
