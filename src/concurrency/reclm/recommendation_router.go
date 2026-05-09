package reclm

import (
	"context"

	"omni-engines/core/result"
)

type RecQuery struct {
	UserID     string
	Candidates []string
}

func RouteRecommendation(ctx context.Context, q RecQuery) result.Result[[]float64] {
	if len(q.Candidates) == 0 {
		return result.Err[[]float64](nil)
	}
	scores := make([]float64, len(q.Candidates))
	return result.Ok(scores)
}
