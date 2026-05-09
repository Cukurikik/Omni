package mistral

import (
	"context"
	"errors"
)

type VectorResult struct {
	DotProduct float64
	Orthogonal bool
}

type MistralRouter struct {
	Epsilon float64
}

// OMNI Network Layer - Vector Dot Routing
func (r *MistralRouter) ProcessSimilarity(ctx context.Context, dot float64) (*VectorResult, error) {
	// Monadic check
	if r.Epsilon < 0 {
		return nil, errors.New("epsilon cannot be negative")
	}

	isOrtho := dot > -r.Epsilon && dot < r.Epsilon

	return &VectorResult{
		DotProduct: dot,
		Orthogonal: isOrtho,
	}, nil
}
