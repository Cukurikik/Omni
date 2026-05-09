package uot

import (
	"context"

	"omni-engines/core/result"
)

func EvaluateUncertainty(ctx context.Context, entropy float64) result.Result[string] {
	if entropy < 0 {
		return result.Err[string](nil)
	}
	if entropy > 1.0 {
		return result.Ok("SEEK_INFO")
	}
	return result.Ok("ACT")
}
