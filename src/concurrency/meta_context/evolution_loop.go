package meta_context

import (
	"context"
	"github.com/omni/core/result"
)

func RunEvolutionEpoch(ctx context.Context, generation int) result.Result[int] {
	if generation < 0 {
		return result.Err[int](nil)
	}
	return result.Ok(generation + 1)
}
