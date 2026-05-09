package flora_opt

import (
	"context"

	"omni-engines/core/result"
)

func SyncCompressedGradients(ctx context.Context, grads []float32) result.Result[bool] {
	if len(grads) == 0 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
