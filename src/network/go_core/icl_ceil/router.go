package icl_ceil

import (
	"context"
	"errors"
)

type CentroidResult struct {
	UpdatesProcessed int32
	Converged        bool
}

type KRouter struct {
	ConvergenceDelta float64
}

// OMNI Network Layer - Clustering Convergence Router
func (r *KRouter) RouteUpdate(ctx context.Context, shift float64, updates int32) (*CentroidResult, error) {
	if shift < 0 {
		return nil, errors.New("shift delta cannot be negative")
	}
	
	return &CentroidResult{
		UpdatesProcessed: updates,
		Converged:        shift <= r.ConvergenceDelta,
	}, nil
}
