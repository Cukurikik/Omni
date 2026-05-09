package network_go

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"
)

// Request defines an incoming generation request
type Request struct {
	ID        string
	Prompt    string
	MaxTokens int
	Priority  int
}

// Router schedules and distributes requests using RadixAttention awareness (SGLang concept)
type Router struct {
	mu           sync.RWMutex
	workerNodes  []*WorkerClient
	requestQueue chan *Request
	prefixCache  map[string]int // Maps prompt prefixes to node IDs for data locality
}

func NewRouter(queueSize int) *Router {
	return &Router{
		workerNodes:  make([]*WorkerClient, 0),
		requestQueue: make(chan *Request, queueSize),
		prefixCache:  make(map[string]int),
	}
}

func (r *Router) RegisterWorker(client *WorkerClient) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.workerNodes = append(r.workerNodes, client)
	fmt.Printf("OMNI Go (SGLang Router): Registered worker node %s\n", client.NodeID)
}

func (r *Router) SubmitRequest(ctx context.Context, req *Request) error {
	select {
	case r.requestQueue <- req:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	default:
		return errors.New("OMNI Go: Router queue is full, backpressure triggered")
	}
}

func (r *Router) StartEventLoop() {
	go func() {
		for req := range r.requestQueue {
			r.routeRequest(req)
		}
	}()
}

func (r *Router) routeRequest(req *Request) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.workerNodes) == 0 {
		fmt.Printf("OMNI Go Error: Dropping request %s, no workers available\n", req.ID)
		return
	}

	// Radix Tree Prefix Matching Logic (Simplified)
	// Attempts to find a worker that already has the KV cache for this prompt prefix
	targetWorker := r.workerNodes[time.Now().UnixNano()%int64(len(r.workerNodes))] // Fallback: Random/RoundRobin

	for prefix, workerID := range r.prefixCache {
		if len(req.Prompt) >= len(prefix) && req.Prompt[:len(prefix)] == prefix {
			for _, w := range r.workerNodes {
				if w.NodeID == fmt.Sprintf("node-%d", workerID) {
					targetWorker = w
					break
				}
			}
		}
	}

	// Dispatch asynchronously
	go func(worker *WorkerClient, request *Request) {
		err := worker.Process(request)
		if err != nil {
			fmt.Printf("OMNI Go: Worker failed to process request %s: %v\n", request.ID, err)
		} else {
			// Update prefix cache upon success
			r.mu.Lock()
			r.prefixCache[request.Prompt[:min(10, len(request.Prompt))]] = worker.NumericID
			r.mu.Unlock()
		}
	}(targetWorker, req)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

