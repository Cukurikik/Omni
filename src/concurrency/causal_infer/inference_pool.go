package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type InferenceTask struct {
	NodeID      string
	Observation float64
}

type InferencePool struct {
	workers int
	tasks   chan InferenceTask
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewInferencePool(workers int) *InferencePool {
	return &InferencePool{
		workers: workers,
		tasks:   make(chan InferenceTask, 500),
		results: make(chan OmniResult, 500),
	}
}

func (p *InferencePool) Start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *InferencePool) worker(id int) {
	defer p.wg.Done()
	for task := range p.tasks {
		if task.Observation < 0 {
			p.results <- OmniResult{Error: fmt.Errorf("invalid observation %v", task.Observation)}
			continue
		}

		// Deterministic inference calculation
		posterior := (task.Observation * 0.8) / ((task.Observation * 0.8) + (1-task.Observation)*0.2)
		p.results <- OmniResult{Value: fmt.Sprintf("Node %s posterior: %.4f", task.NodeID, posterior)}
	}
}

func (p *InferencePool) Submit(task InferenceTask) {
	p.tasks <- task
}

func (p *InferencePool) Close() {
	close(p.tasks)
	p.wg.Wait()
	close(p.results)
}
