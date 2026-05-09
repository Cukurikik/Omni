// omni_rag_service.go — RAG API Service
// Inspired by: LangChain-RAG-FastAPI-Service
// Layer: Network / Go
//
// High-performance REST/gRPC hybrid service for Retrieval-Augmented Generation,
// managing document chunking, vector DB queries, and LLM augmentation.

package ragservice

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Represents a retrieved document chunk from the vector database.
type Document struct {
	ID       string                 `json:"id"`
	Content  string                 `json:"content"`
	Metadata map[string]interface{} `json:"metadata"`
	Score    float64                `json:"score"`
}

// Request payload for RAG query.
type RAGQueryRequest struct {
	Query           string `json:"query"`
	TopK            int    `json:"top_k"`
	Collection      string `json:"collection"`
	EnableStreaming bool   `json:"stream"`
	Filter          string `json:"filter,omitempty"`
}

// Response payload containing the LLM answer and the sources used.
type RAGQueryResponse struct {
	Answer     string     `json:"answer"`
	Sources    []Document `json:"sources"`
	LatencyMs  int64      `json:"latency_ms"`
	TokensUsed int        `json:"tokens_used"`
}

// Interfaces bridging the network layer to the compute/domain layers.
type VectorStore interface {
	Search(ctx context.Context, collection, query string, topK int, filter string) ([]Document, error)
}

type LLMClient interface {
	GenerateAugmented(ctx context.Context, prompt string, context []Document) (string, int, error)
	GenerateAugmentedStream(ctx context.Context, prompt string, context []Document, out chan<- string) error
}

// The core RAG Service implementation.
type OmniRAGService struct {
	vectorStore VectorStore
	llmClient   LLMClient
	timeout     time.Duration
}

func NewOmniRAGService(vs VectorStore, llm LLMClient) *OmniRAGService {
	return &OmniRAGService{
		vectorStore: vs,
		llmClient:   llm,
		timeout:     30 * time.Second,
	}
}

// HandleQuery processes standard HTTP POST requests for RAG.
func (s *OmniRAGService) HandleQuery(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req RAGQueryRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.Query == "" {
		http.Error(w, "Query is required", http.StatusBadRequest)
		return
	}
	if req.TopK <= 0 {
		req.TopK = 5
	}

	ctx, cancel := context.WithTimeout(r.Context(), s.timeout)
	defer cancel()

	start := time.Now()

	// 1. Retrieve context
	docs, err := s.vectorStore.Search(ctx, req.Collection, req.Query, req.TopK, req.Filter)
	if err != nil {
		http.Error(w, fmt.Sprintf("Vector search failed: %v", err), http.StatusInternalServerError)
		return
	}

	// 2. Stream vs Block generation
	if req.EnableStreaming {
		s.handleStreamingQuery(w, ctx, req, docs)
		return
	}

	// 3. Generate augmented answer
	answer, tokens, err := s.llmClient.GenerateAugmented(ctx, req.Query, docs)
	if err != nil {
		http.Error(w, fmt.Sprintf("LLM generation failed: %v", err), http.StatusInternalServerError)
		return
	}

	resp := RAGQueryResponse{
		Answer:     answer,
		Sources:    docs,
		LatencyMs:  time.Since(start).Milliseconds(),
		TokensUsed: tokens,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func (s *OmniRAGService) handleStreamingQuery(w http.ResponseWriter, ctx context.Context, req RAGQueryRequest, docs []Document) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	// Send initial context meta
	ctxBytes, _ := json.Marshal(map[string]interface{}{"event": "context", "sources": docs})
	fmt.Fprintf(w, "data: %s\n\n", ctxBytes)
	flusher.Flush()

	streamCh := make(chan string)
	errCh := make(chan error, 1)

	go func() {
		errCh <- s.llmClient.GenerateAugmentedStream(ctx, req.Query, docs, streamCh)
	}()

	for {
		select {
		case token, ok := <-streamCh:
			if !ok {
				fmt.Fprintf(w, "data: [DONE]\n\n")
				flusher.Flush()
				return
			}
			msg, _ := json.Marshal(map[string]string{"event": "token", "data": token})
			fmt.Fprintf(w, "data: %s\n\n", msg)
			flusher.Flush()

		case err := <-errCh:
			if err != nil {
				errMsg, _ := json.Marshal(map[string]string{"event": "error", "message": err.Error()})
				fmt.Fprintf(w, "data: %s\n\n", errMsg)
				flusher.Flush()
			}
			return

		case <-ctx.Done():
			return
		}
	}
}
