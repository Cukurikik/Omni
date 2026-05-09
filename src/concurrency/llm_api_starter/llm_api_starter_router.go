package llm_api_starter

import (
	"context"
	"errors"
)

// OMNI Router for: Token bucket rate limiter logic
type llm_api_starterResult struct {
	Success bool
	Status  string
}

type llm_api_starterRouter struct {
	Active bool
}

func Newllm_api_starterRouter() *llm_api_starterRouter {
	return &llm_api_starterRouter{Active: true}
}

func (r *llm_api_starterRouter) Execute(ctx context.Context, data []byte) (*llm_api_starterResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &llm_api_starterResult{
		Success: true,
		Status:  "computed",
	}, nil
}
