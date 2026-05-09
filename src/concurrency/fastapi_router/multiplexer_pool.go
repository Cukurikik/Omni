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

type HttpRequest struct {
	ReqID  string
	Path   string
	Method string
}

type MultiplexerPool struct {
	reqQueue chan HttpRequest
	wg       sync.WaitGroup
}

func NewMultiplexerPool(numWorkers int, bufferSize int) *MultiplexerPool {
	p := &MultiplexerPool{
		reqQueue: make(chan HttpRequest, bufferSize),
	}

	for i := 0; i < numWorkers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}

	return p
}

func (p *MultiplexerPool) worker(workerID int) {
	defer p.wg.Done()

	for req := range p.reqQueue {
		// Simulate routing overhead deterministically
		time.Sleep(2 * time.Millisecond)
		fmt.Printf("FastAPI Router [Worker %d]: Routed %s %s -> Target Handler\n", workerID, req.Method, req.Path)
	}
}

func (p *MultiplexerPool) DispatchRequest(req HttpRequest) OmniResult {
	select {
	case p.reqQueue <- req:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Router 503 Service Unavailable: Queue Full")}
	}
}

func (p *MultiplexerPool) Shutdown() {
	close(p.reqQueue)
	p.wg.Wait()
}
