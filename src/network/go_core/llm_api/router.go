package llm_api

import (
	"context"
	"errors"
)

type RateResult struct {
	Allowed   bool
	Remaining float64
}

type APIRouter struct {
	Capacity float64
}

// OMNI Network Layer - Rate Limiting Router
func (r *APIRouter) RouteRequest(ctx context.Context, requested, remaining float64) (*RateResult, error) {
	if requested < 0 {
		return nil, errors.New("cannot request negative tokens")
	}

	allowed := remaining >= requested
	newRemaining := remaining
	if allowed {
		newRemaining -= requested
	}

	return &RateResult{
		Allowed:   allowed,
		Remaining: newRemaining,
	}, nil
}
