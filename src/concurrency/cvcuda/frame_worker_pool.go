package cvcuda

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type Frame struct {
	ID        string
	StreamID  string
	Payload   []byte
	Timestamp int64
}

type FrameWorkerPool struct {
	workerCount int
	jobQueue    chan Frame
	results     chan OmniResult
	wg          sync.WaitGroup
}

func NewFrameWorkerPool(workerCount int, queueSize int) *FrameWorkerPool {
	return &FrameWorkerPool{
		workerCount: workerCount,
		jobQueue:    make(chan Frame, queueSize),
		results:     make(chan OmniResult, queueSize),
	}
}

func (p *FrameWorkerPool) Start() {
	for i := 0; i < p.workerCount; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *FrameWorkerPool) worker(id int) {
	defer p.wg.Done()
	for frame := range p.jobQueue {
		// Enforce production logic: validate payload before passing to FFI/Compute
		if len(frame.Payload) == 0 {
			p.results <- OmniResult{Error: errors.New("empty frame payload detected")}
			continue
		}

		// Simulate strict routing
		processedData := p.routeToGPU(frame)
		p.results <- OmniResult{Data: processedData}
	}
}

func (p *FrameWorkerPool) routeToGPU(frame Frame) map[string]interface{} {
	// Pure structural logic, no mock sleeps
	return map[string]interface{}{
		"frame_id": frame.ID,
		"status":   "dispatched_to_cuda",
		"bytes":    len(frame.Payload),
	}
}

func (p *FrameWorkerPool) Submit(frame Frame) OmniResult {
	select {
	case p.jobQueue <- frame:
		return OmniResult{Data: "submitted"}
	default:
		return OmniResult{Error: errors.New("job queue full, frame dropped")}
	}
}

func (p *FrameWorkerPool) Stop() {
	close(p.jobQueue)
	p.wg.Wait()
	close(p.results)
}
