package oceangpt

import (
	"context"
	"errors"
)

// OMNI Router for: Acoustic wave root mean square
type oceangptResult struct {
	Success bool
	Status  string
}

type oceangptRouter struct {
	Active bool
}

func NewoceangptRouter() *oceangptRouter {
	return &oceangptRouter{Active: true}
}

func (r *oceangptRouter) Execute(ctx context.Context, data []byte) (*oceangptResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &oceangptResult{
		Success: true,
		Status:  "computed",
	}, nil
}
