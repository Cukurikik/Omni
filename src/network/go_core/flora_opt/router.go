package flora_opt

import (
	"context"
	"errors"
)

type FloraResult struct {
	Norm     float64
	IsStable bool
}

type FloraRouter struct {
	MaxNorm float64
}

// OMNI Network Layer - Stable L2 Norm Routing
func (r *FloraRouter) ProcessNorm(ctx context.Context, norm float64) (*FloraResult, error) {
	if norm < 0 {
		return nil, errors.New("negative norm detected")
	}

	return &FloraResult{
		Norm:     norm,
		IsStable: norm <= r.MaxNorm,
	}, nil
}
