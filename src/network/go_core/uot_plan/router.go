package uot_plan

import (
	"context"
	"errors"
)

type EntropyResult struct {
	Entropy float64
	Certain bool
}

type PlanRouter struct {
	CertainThreshold float64
}

// OMNI Network Layer - Uncertainty Router
func (r *PlanRouter) EvaluateUncertainty(ctx context.Context, entropy float64) (*EntropyResult, error) {
	if entropy < 0 {
		return nil, errors.New("entropy cannot be negative")
	}

	return &EntropyResult{
		Entropy: entropy,
		Certain: entropy <= r.CertainThreshold,
	}, nil
}
