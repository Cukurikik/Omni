package m3exam

import (
	"context"
	"errors"
)

type ScoreResult struct {
	F1Score float64
	Passed  bool
}

type M3Router struct {
	TargetF1 float64
}

// OMNI Network Layer - Metric Scoring Router
func (r *M3Router) EvaluateScore(ctx context.Context, f1 float64) (*ScoreResult, error) {
	if f1 < 0.0 || f1 > 1.0 {
		return nil, errors.New("F1 score must be bounded [0,1]")
	}

	return &ScoreResult{
		F1Score: f1,
		Passed:  f1 >= r.TargetF1,
	}, nil
}
