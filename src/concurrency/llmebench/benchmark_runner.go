package llmebench

import (
	"context"
	"github.com/omni/core/result"
)

func RunDataset(ctx context.Context, datasetID string) result.Result[bool] {
	if datasetID == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
