package advanced_rag

import (
	"context"
	"errors"
)

type BM25Result struct {
	Score float64
	Match bool
}

type RagRouter struct {
	MinScore float64
}

// OMNI Network Layer - RAG Scoring Router
func (r *RagRouter) ProcessBM25(ctx context.Context, score float64) (*BM25Result, error) {
	if score < 0 {
		return nil, errors.New("invalid negative bm25 score")
	}

	return &BM25Result{
		Score: score,
		Match: score >= r.MinScore,
	}, nil
}
