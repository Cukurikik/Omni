package omni_secure

import (
	"context"
	"github.com/omni/core/result"
)

func TerminateTLS(ctx context.Context, raw []byte) result.Result[[]byte] {
	if len(raw) == 0 {
		return result.Err[[]byte](nil)
	}
	return result.Ok(raw)
}
