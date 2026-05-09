package network_gocore

import (
	"encoding/json"
	"sync"
)

// SwarmTelemetryAggregator collects state from physical or virtual swarms
// over UDP/TCP for RL processing.
type SwarmTelemetryAggregator struct {
	mu          sync.RWMutex
	AgentStates map[int]AgentState
}

type AgentState struct {
	ID      int
	X       float64
	Y       float64
	Battery float64
}

func NewSwarmTelemetryAggregator() *SwarmTelemetryAggregator {
	return &SwarmTelemetryAggregator{
		AgentStates: make(map[int]AgentState),
	}
}

func (a *SwarmTelemetryAggregator) UpdateAgent(state AgentState) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.AgentStates[state.ID] = state
}

func (a *SwarmTelemetryAggregator) GetGlobalStateAsJSON() ([]byte, error) {
	a.mu.RLock()
	defer a.mu.RUnlock()
	return json.Marshal(a.AgentStates)
}

