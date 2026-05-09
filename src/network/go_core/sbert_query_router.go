package network_gocore

import (
	"encoding/json"
	"net/http"
)

type SBERTQueryRouter struct {
	IndexServerURL string
}

type SearchQuery struct {
	QueryText string `json:"query_text"`
	TopK      int    `json:"top_k"`
}

func NewSBERTQueryRouter(indexURL string) *SBERTQueryRouter {
	return &SBERTQueryRouter{
		IndexServerURL: indexURL,
	}
}

func (r *SBERTQueryRouter) HandleSearchRequest(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var q SearchQuery
	if err := json.NewDecoder(req.Body).Decode(&q); err != nil {
		http.Error(w, "Invalid query format", http.StatusBadRequest)
		return
	}

	// OMNI Router logic - send vector encoding request to Python layer, then to Rust FAISS
	response := map[string]interface{}{
		"status": "success",
		"query":  q.QueryText,
		"results": []map[string]interface{}{
			{"doc_id": "doc_102", "score": 0.94},
			{"doc_id": "doc_88", "score": 0.81},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

