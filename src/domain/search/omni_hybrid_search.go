// omni_hybrid_search.go — Hybrid Document Retrieval
// Layer: Domain / Go
//
// Combines semantic dense vector search with sparse keyword search (BM25)
// using Reciprocal Rank Fusion (RRF) for highly accurate RAG retrieval.

package search

import (
	"context"
	"sort"
)

type DocumentResult struct {
	ID    string
	Score float32
}

// Interfaces representing the two backend retrieval systems
type DenseRetriever interface {
	SemanticSearch(ctx context.Context, queryVector []float32, topK int) ([]DocumentResult, error)
}

type SparseRetriever interface {
	KeywordSearch(ctx context.Context, queryText string, topK int) ([]DocumentResult, error)
}

type OmniHybridSearcher struct {
	dense  DenseRetriever
	sparse SparseRetriever
}

func NewOmniHybridSearcher(d DenseRetriever, s SparseRetriever) *OmniHybridSearcher {
	return &OmniHybridSearcher{
		dense:  d,
		sparse: s,
	}
}

// Reciprocal Rank Fusion constant
const RRF_K = 60.0

// Search performs both queries concurrently and fuses the results.
func (h *OmniHybridSearcher) Search(ctx context.Context, queryText string, queryVector []float32, topK int) ([]DocumentResult, error) {
	// Execute both searches (mocking concurrency for brevity)
	denseResults, err := h.dense.SemanticSearch(ctx, queryVector, topK*2)
	if err != nil {
		return nil, err
	}

	sparseResults, err := h.sparse.KeywordSearch(ctx, queryText, topK*2)
	if err != nil {
		return nil, err
	}

	return h.fuseResults(denseResults, sparseResults, topK), nil
}

func (h *OmniHybridSearcher) fuseResults(dense []DocumentResult, sparse []DocumentResult, topK int) []DocumentResult {
	scoreMap := make(map[string]float32)

	// Calculate RRF for Dense
	for rank, res := range dense {
		scoreMap[res.ID] += 1.0 / (RRF_K + float32(rank+1))
	}

	// Calculate RRF for Sparse
	for rank, res := range sparse {
		scoreMap[res.ID] += 1.0 / (RRF_K + float32(rank+1))
	}

	// Convert map back to slice
	var fused []DocumentResult
	for id, score := range scoreMap {
		fused = append(fused, DocumentResult{ID: id, Score: score})
	}

	// Sort descending by fused score
	sort.Slice(fused, func(i, j int) bool {
		return fused[i].Score > fused[j].Score
	})

	if len(fused) > topK {
		fused = fused[:topK]
	}

	return fused
}
