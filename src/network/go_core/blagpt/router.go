package blagpt

import (
	"context"
	"errors"
)

type ImpurityResult struct {
	Gini  float64
	Split bool
}

type BlaRouter struct {
	MaxImpurity float64
}

// OMNI Network Layer - BlaGPT Decision Router
func (r *BlaRouter) EvaluateSplit(ctx context.Context, gini float64) (*ImpurityResult, error) {
	if gini < 0.0 || gini > 1.0 {
		return nil, errors.New("gini impurity must be between 0 and 1")
	}

	return &ImpurityResult{
		Gini:  gini,
		Split: gini <= r.MaxImpurity,
	}, nil
}
