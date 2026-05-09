package code_synth

import (
	"context"
	"errors"
)

// OMNI Router for: AST Depth
type code_synthResult struct {
	Success bool
	Status  string
}

type code_synthRouter struct {
	Active bool
}

func Newcode_synthRouter() *code_synthRouter {
	return &code_synthRouter{Active: true}
}

func (r *code_synthRouter) Execute(ctx context.Context, data []byte) (*code_synthResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &code_synthResult{
		Success: true,
		Status:  "computed",
	}, nil
}
