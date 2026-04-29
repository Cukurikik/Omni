package icl_ceil

import (
	"context"
	"github.com/omni/core/result"
)

func RouteExemplars(ctx context.Context, indices []int) result.Result[bool] {
	if len(indices) == 0 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
