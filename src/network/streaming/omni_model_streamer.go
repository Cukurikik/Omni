// omni_model_streamer.go — High-Throughput Model Inference Streamer
// Layer: Network / Go
//
// Handles highly concurrent streaming HTTP requests for generative AI models,
// buffering chunks from the compute layer and flushing them efficiently to clients.

package streaming

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

type StreamChunk struct {
	Content string `json:"content"`
	IsEnd   bool   `json:"is_end"`
}

type SSEPayload struct {
	Choices []struct {
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
	} `json:"choices"`
}

type ModelBackend interface {
	GenerateStream(ctx context.Context, prompt string, chunks chan<- StreamChunk)
}

type StreamingHandler struct {
	backend ModelBackend
	wg      sync.WaitGroup
}

func NewStreamingHandler(backend ModelBackend) *StreamingHandler {
	return &StreamingHandler{
		backend: backend,
	}
}

func (h *StreamingHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Require POST
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Setup SSE headers
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	prompt := r.URL.Query().Get("prompt") // Simplification for demo
	if prompt == "" {
		prompt = "Default prompt"
	}

	chunkChan := make(chan StreamChunk, 50)

	// Start inference in a goroutine
	h.wg.Add(1)
	go func() {
		defer h.wg.Done()
		defer close(chunkChan)
		h.backend.GenerateStream(r.Context(), prompt, chunkChan)
	}()

	// Stream to client
	for chunk := range chunkChan {
		if chunk.IsEnd {
			fmt.Fprintf(w, "data: [DONE]\n\n")
			flusher.Flush()
			break
		}

		payload := SSEPayload{}
		payload.Choices = []struct {
			Delta struct {
				Content string `json:"content"`
			} `json:"delta"`
		}{{Delta: struct {
			Content string `json:"content"`
		}{Content: chunk.Content}}}

		jsonData, err := json.Marshal(payload)
		if err != nil {
			log.Printf("JSON serialization error: %v", err)
			continue
		}

		fmt.Fprintf(w, "data: %s\n\n", string(jsonData))
		flusher.Flush()
	}

	// Wait for backend to clean up
	h.wg.Wait()
}

// Mock backend for testing compilation without full engine bindings
type MockBackend struct{}

func (m *MockBackend) GenerateStream(ctx context.Context, prompt string, chunks chan<- StreamChunk) {
	words := []string{"Hello", " from", " OMNI", " stream", " engine!"}
	for _, w := range words {
		select {
		case <-ctx.Done():
			return
		case <-time.After(100 * time.Millisecond):
			chunks <- StreamChunk{Content: w, IsEnd: false}
		}
	}
	chunks <- StreamChunk{Content: "", IsEnd: true}
}

