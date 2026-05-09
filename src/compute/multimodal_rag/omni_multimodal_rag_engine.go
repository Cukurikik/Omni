// OMNI FRAMEWORK: BATCH 1 SEMESTER 14
// ENGINE: OMNI MULTIMODAL RAG ENGINE
// DOMAIN: COMPUTE / NLP & VISION (GO)
// ZERO MOCK - PRODUCTION READY
// ==========================================

package multimodal_rag

import (
	"context"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
)

// RAGError defines custom error structures for retrieval operations.
type RAGError struct {
	Code    string
	Message string
	Err     error
}

func (e *RAGError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("RAGError[%s]: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("RAGError[%s]: %s", e.Code, e.Message)
}

// Result is the standard OMNI monadic result.
type RAGResult[T any] struct {
	Value T
	Err   error
}

// Document represents a multimodal chunk (text + image features).
type Document struct {
	ID        string
	Text      string
	Embedding []float64 // CLIP or Text embedding
	Modality  string    // "text", "image", "multimodal"
}

// OmniMultimodalRAGEngine orchestrates cross-modal vector retrieval.
type OmniMultimodalRAGEngine struct {
	mu         sync.RWMutex
	collection []Document
	dim        int

	// Metrics
	docsIndexed atomic.Int64
	queriesDone atomic.Int64
}

// NewOmniMultimodalRAGEngine initializes the retrieval engine.
func NewOmniMultimodalRAGEngine(vectorDim int) *OmniMultimodalRAGEngine {
	return &OmniMultimodalRAGEngine{
		collection: make([]Document, 0),
		dim:        vectorDim,
	}
}

// AddDocument ingests a multimodal document into the index. O(1).
func (e *OmniMultimodalRAGEngine) AddDocument(doc Document) RAGResult[bool] {
	if len(doc.Embedding) != e.dim {
		return RAGResult[bool]{Err: &RAGError{Code: "DIM_MISMATCH", Message: "Embedding dimension does not match index"}}
	}

	e.mu.Lock()
	defer e.mu.Unlock()

	e.collection = append(e.collection, doc)
	e.docsIndexed.Add(1)

	return RAGResult[bool]{Value: true}
}

// cosineSimilarity calculates similarity between two vectors.
func cosineSimilarity(a, b []float64) float64 {
	var dot, normA, normB float64
	for i := range a {
		dot += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}
	if normA == 0 || normB == 0 {
		return 0
	}
	return dot / (math.Sqrt(normA) * math.Sqrt(normB))
}

// Retrieve searches the vector space for the top K closest multimodal documents.
func (e *OmniMultimodalRAGEngine) Retrieve(ctx context.Context, queryEmbedding []float64, topK int) RAGResult[[]Document] {
	if len(queryEmbedding) != e.dim {
		return RAGResult[[]Document]{Err: &RAGError{Code: "DIM_MISMATCH", Message: "Query dimension does not match index"}}
	}

	e.mu.RLock()
	defer e.mu.RUnlock()

	e.queriesDone.Add(1)

	type scoredDoc struct {
		doc   Document
		score float64
	}

	var results []scoredDoc
	for _, d := range e.collection {
		select {
		case <-ctx.Done():
			return RAGResult[[]Document]{Err: ctx.Err()}
		default:
		}

		score := cosineSimilarity(queryEmbedding, d.Embedding)
		results = append(results, scoredDoc{doc: d, score: score})
	}

	// Simple sort for Top K
	if topK > len(results) {
		topK = len(results)
	}
	for i := 0; i < topK; i++ {
		maxIdx := i
		for j := i + 1; j < len(results); j++ {
			if results[j].score > results[maxIdx].score {
				maxIdx = j
			}
		}
		results[i], results[maxIdx] = results[maxIdx], results[i]
	}

	out := make([]Document, topK)
	for i := 0; i < topK; i++ {
		out[i] = results[i].doc
	}

	return RAGResult[[]Document]{Value: out}
}

// Diagnostics returns system state metrics.
func (e *OmniMultimodalRAGEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":       "OmniMultimodalRAGEngine",
		"version":      "1.0.0-production",
		"docs_indexed": e.docsIndexed.Load(),
		"queries_done": e.queriesDone.Load(),
		"vector_dim":   e.dim,
		"status":       "operational",
	}
}
