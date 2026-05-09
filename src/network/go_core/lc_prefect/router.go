package lc_prefect

import (
	"context"
	"errors"
)

type DAGResult struct {
	MaxDepth int32
	Valid    bool
}

type PrefectRouter struct {
	MaxAllowedDepth int32
}

// OMNI Network Layer - DAG Validation
func (r *PrefectRouter) ProcessGraph(ctx context.Context, depth int32) (*DAGResult, error) {
	if depth < 0 {
		return nil, errors.New("negative graph depth is invalid")
	}

	return &DAGResult{
		MaxDepth: depth,
		Valid:    depth <= r.MaxAllowedDepth,
	}, nil
}
