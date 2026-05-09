package camel_agents

import (
	"context"
	"sync"

	"omni-engines/core/result"
)

type AgentWorker struct {
	ID   string
	Role string
}

type AgentPool struct {
	workers map[string]*AgentWorker
	mu      sync.RWMutex
}

func NewAgentPool() *AgentPool {
	return &AgentPool{workers: make(map[string]*AgentWorker)}
}

func (p *AgentPool) DispatchTask(ctx context.Context, agentID string, task []byte) result.Result[bool] {
	p.mu.RLock()
	defer p.mu.RUnlock()
	if _, exists := p.workers[agentID]; !exists {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}
