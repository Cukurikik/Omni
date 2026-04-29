package omni_cache

import (
	"context"
	"github.com/omni/core/result"
)

func SetCacheItem(ctx context.Context, key, val string) result.Result[bool] {
	if key == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
