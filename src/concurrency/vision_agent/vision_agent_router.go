package vision_agent

import (
	"context"
	"errors"
)

// OMNI Router for: Sobel magnitude
type vision_agentResult struct {
	Success bool
	Status  string
}

type vision_agentRouter struct {
	Active bool
}

func Newvision_agentRouter() *vision_agentRouter {
	return &vision_agentRouter{Active: true}
}

func (r *vision_agentRouter) Execute(ctx context.Context, data []byte) (*vision_agentResult, error) {
	if len(data) == 0 {
		return nil, errors.New("empty payload provided")
	}
	if !r.Active {
		return nil, errors.New("router is inactive")
	}

	return &vision_agentResult{
		Success: true,
		Status:  "computed",
	}, nil
}
