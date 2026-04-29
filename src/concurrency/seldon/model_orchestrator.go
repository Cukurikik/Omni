package seldon

import (
	"time"
	"fmt"
	"context"
	"sync"
)

// OMNI Go Concurrency Layer: Seldon Model Orchestrator
// Thread-safe routing and circuit breaking for Seldon-core ML deployments.

type SeldonDeployment struct {
	ID         string
	Endpoint   string
	IsActive   bool
	mu         sync.RWMutex
}

type Orchestrator struct {
	deployments map[string]*SeldonDeployment
	routerMu    sync.RWMutex
}

func NewOrchestrator() *Orchestrator {
	return &Orchestrator{
		deployments: make(map[string]*SeldonDeployment),
	}
}

func (o *Orchestrator) RegisterDeployment(id string, endpoint string) error {
	o.routerMu.Lock()
	defer o.routerMu.Unlock()

	if _, exists := o.deployments[id]; exists {
		return fmt.Errorf("deployment %s already registered", id)
	}

	o.deployments[id] = &SeldonDeployment{
		ID:       id,
		Endpoint: endpoint,
		IsActive: true,
	}
	return nil
}

func (o *Orchestrator) RouteInference(ctx context.Context, depID string, payload []byte) ([]byte, error) {
	o.routerMu.RLock()
	dep, exists := o.deployments[depID]
	o.routerMu.RUnlock()

	if !exists {
		return nil, fmt.Errorf("deployment %s not found", depID)
	}

	dep.mu.RLock()
	active := dep.IsActive
	endpoint := dep.Endpoint
	dep.mu.RUnlock()

	if !active {
		return nil, fmt.Errorf("deployment %s is currently inactive or cordoned", depID)
	}

	// Simulated high-speed network call to gRPC endpoint
	select {
	case <-time.After(10 * time.Millisecond): // Simulation of inference latency
		// In production, this would be a gRPC call to `endpoint`
		result := []byte(fmt.Sprintf("{\"status\":\"success\",\"model\":\"%s\"}", depID))
		return result, nil
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

func (o *Orchestrator) CordonDeployment(id string) error {
	o.routerMu.RLock()
	dep, exists := o.deployments[id]
	o.routerMu.RUnlock()

	if !exists {
		return fmt.Errorf("deployment %s not found", id)
	}

	dep.mu.Lock()
	dep.IsActive = false
	dep.mu.Unlock()
	return nil
}
