package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type ComputeTask struct {
	MatrixSize int
	Iterations int
}

type ComputePool struct {
	workers int
	tasks   chan ComputeTask
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewComputePool(workers int) *ComputePool {
	return &ComputePool{
		workers: workers,
		tasks:   make(chan ComputeTask, 100),
		results: make(chan OmniResult, 100),
	}
}

func (p *ComputePool) Start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *ComputePool) worker(id int) {
	defer p.wg.Done()
	for task := range p.tasks {
		if task.MatrixSize <= 0 || task.Iterations <= 0 {
			p.results <- OmniResult{Error: fmt.Errorf("invalid matrix parameters")}
			continue
		}
		
		// Deterministic FLOPS computation simulation
		flops := float64(task.MatrixSize) * float64(task.MatrixSize) * float64(task.Iterations) * 2.0
		gflops := flops / 1e9
		p.results <- OmniResult{Value: fmt.Sprintf("Worker %d executed %.4f GFLOPS", id, gflops)}
	}
}

func (p *ComputePool) Submit(task ComputeTask) {
	p.tasks <- task
}

func (p *ComputePool) Close() {
	close(p.tasks)
	p.wg.Wait()
	close(p.results)
}
