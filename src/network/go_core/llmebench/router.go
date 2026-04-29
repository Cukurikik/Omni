package llmebench

import (
	"context"
	"errors"
)

type BleuResult struct {
	Penalty float64
	Passed  bool
}

type BenchRouter struct {
	MinPenalty float64
}

// OMNI Network Layer - LLMeBench Evaluation Router
func (r *BenchRouter) EvaluatePenalty(ctx context.Context, penalty float64) (*BleuResult, error) {
	if penalty < 0.0 || penalty > 1.0 {
		return nil, errors.New("brevity penalty must be bounded [0,1]")
	}
	
	return &BleuResult{
		Penalty: penalty,
		Passed:  penalty >= r.MinPenalty,
	}, nil
}
