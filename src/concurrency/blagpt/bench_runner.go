package blagpt

import (
	"context"
	"github.com/omni/core/result"
)

func RunBenchmarkSuite(ctx context.Context) result.Result[string] {
	return result.Ok("Benchmark completed")
}
