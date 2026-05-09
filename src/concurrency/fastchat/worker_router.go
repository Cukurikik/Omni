package fastchat

import (
	"context"
	"fmt"
	"sync"
)

// OMNI FASTCHAT: Worker Router
// Go component mapping chat generation requests to the least loaded model worker in a distributed setup.
// Source: lm-sys/FastChat

type WorkerStatus string

const (
	StatusOnline  WorkerStatus = "ONLINE"
	StatusOffline WorkerStatus = "OFFLINE"
	StatusBusy    WorkerStatus = "BUSY"
)

type WorkerNode struct {
	ID        string
	ModelName string
	Status    WorkerStatus
	Load      int // e.g., active concurrent requests
}

type RouterError struct {
	Message string
}

func (e *RouterError) Error() string { return e.Message }

type WorkerRouter struct {
	mu      sync.RWMutex
	workers map[string]*WorkerNode
}

func NewWorkerRouter() *WorkerRouter {
	return &WorkerRouter{
		workers: make(map[string]*WorkerNode),
	}
}

func (r *WorkerRouter) RegisterWorker(id string, modelName string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.workers[id] = &WorkerNode{
		ID:        id,
		ModelName: modelName,
		Status:    StatusOnline,
		Load:      0,
	}
}

func (r *WorkerRouter) UnregisterWorker(id string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	delete(r.workers, id)
}

func (r *WorkerRouter) UpdateLoad(id string, load int) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if worker, exists := r.workers[id]; exists {
		worker.Load = load
	}
}

// Selects the worker with the lowest load for a specific model
func (r *WorkerRouter) RouteRequest(ctx context.Context, modelName string) (*WorkerNode, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var bestWorker *WorkerNode
	minLoad := int(^uint(0) >> 1) // Max int

	for _, worker := range r.workers {
		if worker.ModelName == modelName && worker.Status == StatusOnline {
			if worker.Load < minLoad {
				minLoad = worker.Load
				bestWorker = worker
			}
		}
	}

	if bestWorker == nil {
		return nil, &RouterError{fmt.Sprintf("No online workers found for model: %s", modelName)}
	}

	return bestWorker, nil
}
