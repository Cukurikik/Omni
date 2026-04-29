package reflect

import (
	"context"
	"github.com/omni/core/result"
)

func ProcessRobotTelemetry(ctx context.Context, data []byte) result.Result[bool] {
	if len(data) == 0 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
