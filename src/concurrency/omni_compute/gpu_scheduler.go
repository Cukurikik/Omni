package omni_compute

import (
	"context"

	"omni-engines/core/result"
)

func ScheduleGPUJob(ctx context.Context, jobID string) result.Result[bool] {
	if jobID == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
