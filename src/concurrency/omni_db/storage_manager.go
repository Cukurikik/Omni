package omni_db

import (
	"context"

	"omni-engines/core/result"
)

func WritePageData(ctx context.Context, path string, data []byte) result.Result[bool] {
	if len(data) == 0 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
