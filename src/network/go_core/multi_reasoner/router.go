package multi_reasoner

import (
	"context"
	"errors"
)

type KLResult struct {
	Divergence float64
	Similar    bool
}

type ReasonRouter struct {
	MaxDivergence float64
}

// OMNI Network Layer - Reasoner KL Divergence Router
func (r *ReasonRouter) RouteDivergence(ctx context.Context, kl float64) (*KLResult, error) {
	if kl < 0 {
		return nil, errors.New("KL divergence cannot be negative")
	}
	
	return &KLResult{
		Divergence: kl,
		Similar:    kl <= r.MaxDivergence,
	}, nil
}
