package langchain_prefect

import (
	"context"

	"omni-engines/core/result"
)

func ExecuteLangchainFlow(ctx context.Context, flowID string) result.Result[bool] {
	if flowID == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
