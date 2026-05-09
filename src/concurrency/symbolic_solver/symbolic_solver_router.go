package symbolic_solver

import (
	"context"
	"errors"
)

// OMNI Router for: RPN simplified pop
type symbolic_solverResult struct {
	Success bool
	Status  string
}

type symbolic_solverRouter struct {
	Active bool
}

func Newsymbolic_solverRouter() *symbolic_solverRouter {
	return &symbolic_solverRouter{Active: true}
}

func (r *symbolic_solverRouter) Execute(ctx context.Context, data []byte) (*symbolic_solverResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &symbolic_solverResult{
		Success: true,
		Status:  "computed",
	}, nil
}
