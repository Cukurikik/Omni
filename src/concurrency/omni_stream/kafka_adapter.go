package omni_stream

import (
	"context"

	"omni-engines/core/result"
)

func PublishMessage(ctx context.Context, topic string, msg []byte) result.Result[bool] {
	if topic == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
