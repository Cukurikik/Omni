package network

import (
	"errors"
	"github.com/omni/core/monads"
)

type MultiAgentGateway struct {
	ActiveAgents int
}

func (m *MultiAgentGateway) RouteTask(taskID string) monads.Result[string] {
	if taskID == "" {
		return monads.Err[string](errors.New("invalid task id"))
	}
	return monads.Ok("Routed to agent network")
}
