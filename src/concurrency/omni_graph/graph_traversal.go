package omni_graph

import (
	"context"
	"github.com/omni/core/result"
)

func TraverseGraph(ctx context.Context, startNodeID int) result.Result[[]int] {
	if startNodeID < 0 {
		return result.Err[[]int](nil)
	}
	return result.Ok([]int{startNodeID})
}
