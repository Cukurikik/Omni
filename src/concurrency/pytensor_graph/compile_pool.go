package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type CompileJob struct {
	GraphID string
	Nodes   int
}

type CompilePool struct {
	jobs    chan CompileJob
	results chan string
	wg      sync.WaitGroup
}

func NewCompilePool(numWorkers int, bufferSize int) *CompilePool {
	pool := &CompilePool{
		jobs:    make(chan CompileJob, bufferSize),
		results: make(chan string, bufferSize),
	}

	for i := 0; i < numWorkers; i++ {
		pool.wg.Add(1)
		go pool.worker()
	}

	return pool
}

func (p *CompilePool) worker() {
	defer p.wg.Done()
	for job := range p.jobs {
		// Deterministic graph compilation latency simulation based on node count
		// In a real scenario, this invokes the C FFI generator
		status := fmt.Sprintf("Graph %s compiled (%d nodes) -> Native Kernel", job.GraphID, job.Nodes)
		p.results <- status
	}
}

func (p *CompilePool) SubmitGraph(job CompileJob) OmniResult {
	p.jobs <- job
	return OmniResult{Value: true}
}

func (p *CompilePool) WaitAndCollect() OmniResult {
	close(p.jobs)
	p.wg.Wait()
	close(p.results)

	var allStatus []string
	for res := range p.results {
		allStatus = append(allStatus, res)
	}

	return OmniResult{Value: allStatus}
}
