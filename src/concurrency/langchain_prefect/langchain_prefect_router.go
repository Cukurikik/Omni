package langchain_prefect

import (
	"context"
	"errors"
)

// OMNI Router for: DAG acyclic depth
type langchain_prefectResult struct {
	Success bool
	Status  string
}

type langchain_prefectRouter struct {
	Active bool
}

func Newlangchain_prefectRouter() *langchain_prefectRouter {
	return &langchain_prefectRouter{Active: true}
}

func (r *langchain_prefectRouter) Execute(ctx context.Context, data []byte) (*langchain_prefectResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &langchain_prefectResult{
		Success: true,
		Status:  "computed",
	}, nil
}
