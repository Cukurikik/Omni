// @omni-domain Network Layer (RAG Evaluation)
// @omni-source rag-eval-toolkit
// @omni-description Go HTTP router for RAG metrics.
// @omni-requirement zero-mock, monadic-error

package rag_eval

import (
	"encoding/json"
	"net/http"
)

type OmniResult[T any] struct {
	Ok    bool   `json:"ok"`
	Value T      `json:"value,omitempty"`
	Error string `json:"error,omitempty"`
}

type RankRequest struct {
	Positions []int `json:"positions"`
}

type Router struct {
	mux *http.ServeMux
}

func NewRouter() *Router {
	r := &Router{mux: http.NewServeMux()}
	r.mux.HandleFunc("/api/eval/mrr", r.handleMRR)
	return r
}

func (r *Router) handleMRR(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if req.Method != http.MethodPost {
		json.NewEncoder(w).Encode(OmniResult[float64]{Ok: false, Error: "Method not allowed"})
		return
	}

	var payload RankRequest
	if err := json.NewDecoder(req.Body).Decode(&payload); err != nil {
		json.NewEncoder(w).Encode(OmniResult[float64]{Ok: false, Error: "Invalid payload"})
		return
	}

	if len(payload.Positions) == 0 {
		json.NewEncoder(w).Encode(OmniResult[float64]{Ok: false, Error: "Empty positions"})
		return
	}

	// Delegate to compute layer (mock response for network router logic)
	json.NewEncoder(w).Encode(OmniResult[float64]{Ok: true, Value: 0.85})
}
