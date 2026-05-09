package gpt4all_unity

import (
	"context"

	"omni-engines/core/result"
)

func RegisterUnityModel(ctx context.Context, path string) result.Result[string] {
	if path == "" {
		return result.Err[string](nil)
	}
	return result.Ok("Registered")
}
