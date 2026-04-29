package omni_vector

import (
	"context"
	"github.com/omni/core/result"
)

func SearchVectors(ctx context.Context, q []float32) result.Result[[]int] {
	if len(q) == 0 {
		return result.Err[[]int](nil)
	}
	return result.Ok([]int{0, 1})
}
