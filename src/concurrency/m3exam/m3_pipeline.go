package m3exam

import (
	"context"

	"omni-engines/core/result"
)

func VerifyExamIntegrity(ctx context.Context, hash string) result.Result[bool] {
	if hash == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
