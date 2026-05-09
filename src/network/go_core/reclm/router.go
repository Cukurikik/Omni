package reclm

import (
	"context"
	"errors"
	"math"
)

type RecResult struct {
	Score float64
	Valid bool
}

type RecRouter struct {
	Threshold float64
}

// OMNI Network Layer - Recommendation BPR Score Evaluator
func (r *RecRouter) EvaluateScore(ctx context.Context, posScore, negScore float64) (*RecResult, error) {
	if math.IsNaN(posScore) || math.IsNaN(negScore) {
		return nil, errors.New("invalid NaN scores provided")
	}

	diff := posScore - negScore
	sigmoid := 1.0 / (1.0 + math.Exp(-diff))

	return &RecResult{
		Score: sigmoid,
		Valid: sigmoid >= r.Threshold,
	}, nil
}
