package alpharec

import (
	"context"
	"errors"
)

type AlphaResult struct {
	Correlation  float64
	IsCorrelated bool
}

type AlphaRouter struct {
	Threshold float64
}

// OMNI Network Layer - Correlation Router
func (r *AlphaRouter) RouteCorrelation(ctx context.Context, score float64) (*AlphaResult, error) {
	if score < -1.0 || score > 1.0 {
		return nil, errors.New("correlation score out of bounds [-1, 1]")
	}

	return &AlphaResult{
		Correlation:  score,
		IsCorrelated: score >= r.Threshold,
	}, nil
}
