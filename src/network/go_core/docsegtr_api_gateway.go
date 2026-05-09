package network_gocore

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

// DocSegTrAPIGateway provides an HTTP endpoint for document segmentation requests.
type DocSegTrAPIGateway struct {
	port int
}

type SegmentationRequest struct {
	DocumentID string `json:"document_id"`
	ImageURL   string `json:"image_url"`
}

func NewDocSegTrAPIGateway(port int) *DocSegTrAPIGateway {
	return &DocSegTrAPIGateway{port: port}
}

func (g *DocSegTrAPIGateway) StartServer(ctx context.Context) error {
	mux := http.NewServeMux()

	mux.HandleFunc("/api/v1/segment", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req SegmentationRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// Simulate routing to compute layer
		resp := map[string]interface{}{
			"status": "processing",
			"job_id": fmt.Sprintf("job_%s", req.DocumentID),
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	})

	addr := fmt.Sprintf(":%d", g.port)
	// Server startup logic
	go func() {
		_ = http.ListenAndServe(addr, mux)
	}()

	return nil
}

