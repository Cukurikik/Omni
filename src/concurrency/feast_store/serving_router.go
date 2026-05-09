package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type FeatureRequest struct {
	EntityID string
	Features []string
	Response chan string
}

type ServingRouter struct {
	reqQueue chan FeatureRequest
	wg       sync.WaitGroup
}

func NewServingRouter(numWorkers int, queueSize int) *ServingRouter {
	r := &ServingRouter{
		reqQueue: make(chan FeatureRequest, queueSize),
	}

	for i := 0; i < numWorkers; i++ {
		r.wg.Add(1)
		go r.worker()
	}

	return r
}

func (r *ServingRouter) worker() {
	defer r.wg.Done()

	for req := range r.reqQueue {
		// Deterministic routing simulation using consistent hashing pattern
		// In reality, this would call the Redis FFI C layer
		time.Sleep(10 * time.Millisecond) // Simulated network/FFI latency

		res := fmt.Sprintf("OK:[%s] -> %d features", req.EntityID, len(req.Features))
		req.Response <- res
	}
}

func (r *ServingRouter) ServeFeatures(entityID string, features []string) OmniResult {
	resChan := make(chan string, 1)

	select {
	case r.reqQueue <- FeatureRequest{EntityID: entityID, Features: features, Response: resChan}:
		val := <-resChan
		return OmniResult{Value: val}
	case <-time.After(50 * time.Millisecond):
		return OmniResult{Error: fmt.Errorf("Timeout: Serving queue saturated")}
	}
}

func (r *ServingRouter) Shutdown() {
	close(r.reqQueue)
	r.wg.Wait()
}
