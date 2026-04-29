package omni_vision

import (
	"context"
	"github.com/omni/core/result"
)

func StreamFrame(ctx context.Context, frameData []byte) result.Result[bool] {
	if len(frameData) == 0 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
