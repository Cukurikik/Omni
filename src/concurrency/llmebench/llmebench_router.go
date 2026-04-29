package llmebench

import (
	"context"
	"errors"
)

// OMNI Router for: BLEU score brevity penalty
type llmebenchResult struct {
	Success bool
	Status  string
}

type llmebenchRouter struct {
	Active bool
}

func NewllmebenchRouter() *llmebenchRouter {
	return &llmebenchRouter{Active: true}
}

func (r *llmebenchRouter) Execute(ctx context.Context, data []byte) (*llmebenchResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}
	
	return &llmebenchResult{
		Success: true,
		Status:  "computed",
	}, nil
}