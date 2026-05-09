package rag_evaluator

import (
	"context"
	"errors"
)

// OMNI Router for: Mean Reciprocal Rank
type rag_evaluatorResult struct {
	Success bool
	Status  string
}

type rag_evaluatorRouter struct {
	Active bool
}

func Newrag_evaluatorRouter() *rag_evaluatorRouter {
	return &rag_evaluatorRouter{Active: true}
}

func (r *rag_evaluatorRouter) Execute(ctx context.Context, data []byte) (*rag_evaluatorResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &rag_evaluatorResult{
		Success: true,
		Status:  "computed",
	}, nil
}
