package knowledge_harvest

import (
	"context"
	"github.com/omni/core/result"
)

type KGEdge struct {
	Subject string
	Predicate string
	Object string
	Weight float64
}

func InsertKGEdge(ctx context.Context, edge KGEdge) result.Result[bool] {
	if edge.Subject == "" || edge.Object == "" {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
