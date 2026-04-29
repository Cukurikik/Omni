// OMNI Network Layer - Ollama REST API
package network

import (
	"errors"
	"net/http"
)

type RestResult struct {
	Configured bool
	Err        error
}

func InitOllamaRouter(address string) RestResult {
	if address == "" {
		return RestResult{Configured: false, Err: errors.New("invalid bind address")}
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/api/generate", func(w http.ResponseWriter, r *http.Request) {})

	return RestResult{Configured: true, Err: nil}
}
