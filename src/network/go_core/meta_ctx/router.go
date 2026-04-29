package meta_ctx

import (
	"context"
	"errors"
)

type EditResult struct {
	Distance int32
	Match    bool
}

type MetaRouter struct {
	MaxDistance int32
}

// OMNI Network Layer - Edit Distance Router
func (r *MetaRouter) RouteEdit(ctx context.Context, distance int32) (*EditResult, error) {
	if distance < 0 {
		return nil, errors.New("edit distance cannot be negative")
	}
	
	return &EditResult{
		Distance: distance,
		Match:    distance <= r.MaxDistance,
	}, nil
}
