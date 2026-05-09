package llmebench

import (
	"context"

	"omni-engines/core/result"
)

func RunDataset(ctx context.Context, datasetID string) result.Result[bool] {
	if datasetID == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
