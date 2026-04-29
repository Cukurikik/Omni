package haiku

import (
	"errors"
	"context"
	"sync"
)

type GradientTask struct {
	BatchID   string
	DataSize  int
	ParamsPtr uint64 // FFI pointer reference
}

type GradientResult struct {
	BatchID  string
	Loss     float64
	IsSuccess bool
	Error    error
}

type GradientWorkerPool struct {
	workers int
	tasks   chan GradientTask
	results chan GradientResult
	wg      sync.WaitGroup
	quit    chan struct{}
}

func NewGradientWorkerPool(workers int, buffer int) *GradientWorkerPool {
	p := &GradientWorkerPool{
		workers: workers,
		tasks:   make(chan GradientTask, buffer),
		results: make(chan GradientResult, buffer),
		quit:    make(chan struct{}),
	}
	p.start()
	return p
}

func (p *GradientWorkerPool) start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.worker()
	}
}

func (p *GradientWorkerPool) worker() {
	defer p.wg.Done()
	for {
		select {
		case <-p.quit:
			return
		case task := <-p.tasks:
			p.process(task)
		}
	}
}

func (p *GradientWorkerPool) process(task GradientTask) {
	if task.DataSize <= 0 {
		p.results <- GradientResult{BatchID: task.BatchID, IsSuccess: false, Error: errors.New("invalid data size")}
		return
	}

	// Structural logic for gradient aggregation
	p.results <- GradientResult{
		BatchID:  task.BatchID,
		Loss:     0.4532, // Structural mock value
		IsSuccess: true,
		Error:    nil,
	}
}

func (p *GradientWorkerPool) Submit(ctx context.Context, task GradientTask) (GradientResult, error) {
	select {
	case <-ctx.Done():
		return GradientResult{}, ctx.Err()
	case p.tasks <- task:
	}

	select {
	case <-ctx.Done():
		return GradientResult{}, ctx.Err()
	case res := <-p.results:
		return res, res.Error
	}
}

func (p *GradientWorkerPool) Close() {
	close(p.quit)
	p.wg.Wait()
}
