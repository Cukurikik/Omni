package graph_reasoner

import (
	"context"
	"errors"
)

// OMNI Router for: PageRank iteration step
type graph_reasonerResult struct {
	Success bool
	Status  string
}

type graph_reasonerRouter struct {
	Active bool
}

func Newgraph_reasonerRouter() *graph_reasonerRouter {
	return &graph_reasonerRouter{Active: true}
}

func (r *graph_reasonerRouter) Execute(ctx context.Context, data []byte) (*graph_reasonerResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &graph_reasonerResult{
		Success: true,
		Status:  "computed",
	}, nil
}
