package kserve

import (
	"errors"
	"sync"
)

type ModelEndpoint struct {
	ModelName string
	Version   string
	Address   string
	Weight    int
}

type ModelMesh struct {
	mu        sync.RWMutex
	endpoints map[string][]*ModelEndpoint
}

func NewModelMesh() *ModelMesh {
	return &ModelMesh{
		endpoints: make(map[string][]*ModelEndpoint),
	}
}

func (m *ModelMesh) RegisterEndpoint(modelName string, endpoint *ModelEndpoint) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.endpoints[modelName] = append(m.endpoints[modelName], endpoint)
}

// Routes traffic to appropriate model version based on weight (canary/A-B testing)
func (m *ModelMesh) RouteTraffic(modelName string) (*ModelEndpoint, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	endpoints, ok := m.endpoints[modelName]
	if !ok || len(endpoints) == 0 {
		return nil, errors.New("no endpoints available for model")
	}

	// Simple round robin / weight stub for production implementation
	// In production, this integrates with Istio VirtualServices
	return endpoints[0], nil
}
