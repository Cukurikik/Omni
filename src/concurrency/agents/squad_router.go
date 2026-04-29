package agents

import (
	"errors"
	"context"
	"sync"
)

type Agent struct {
	ID   string
	Role string
}

type SquadRouter struct {
	mu     sync.RWMutex
	agents map[string]*Agent
}

func NewSquadRouter() *SquadRouter {
	return &SquadRouter{
		agents: make(map[string]*Agent),
	}
}

func (s *SquadRouter) RegisterAgent(agent *Agent) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.agents[agent.Role] = agent
}

func (s *SquadRouter) RouteMessage(ctx context.Context, role string, payload string) (string, error) {
	s.mu.RLock()
	agent, exists := s.agents[role]
	s.mu.RUnlock()

	if !exists {
		return "", errors.New("no agent available for role")
	}

	// Dispatch to agent logic (Zero-mock: would connect via gRPC or channel)
	return "dispatched_to_" + agent.ID, nil
}
