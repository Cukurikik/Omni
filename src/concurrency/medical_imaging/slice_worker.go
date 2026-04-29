package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SliceTask struct {
	ScanID    string
	SliceIdx  int
	Intensity float64
}

type SliceWorker struct {
	workers int
	tasks   chan SliceTask
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewSliceWorker(workers int) *SliceWorker {
	return &SliceWorker{
		workers: workers,
		tasks:   make(chan SliceTask, 1000),
		results: make(chan OmniResult, 1000),
	}
}

func (w *SliceWorker) Start() {
	for i := 0; i < w.workers; i++ {
		w.wg.Add(1)
		go w.process(i)
	}
}

func (w *SliceWorker) process(id int) {
	defer w.wg.Done()
	for task := range w.tasks {
		if task.Intensity < 0 || task.Intensity > 255 {
			w.results <- OmniResult{Error: fmt.Errorf("invalid intensity %.2f", task.Intensity)}
			continue
		}
		
		// Deterministic filtering mathematical simulation
		normalized := task.Intensity / 255.0
		contrastEnhanced := normalized * normalized // simple curve
		
		w.results <- OmniResult{Value: fmt.Sprintf("Worker %d | Scan %s Slice %d | Enhanced: %.4f", id, task.ScanID, task.SliceIdx, contrastEnhanced)}
	}
}

func (w *SliceWorker) Submit(task SliceTask) {
	w.tasks <- task
}

func (w *SliceWorker) Close() {
	close(w.tasks)
	w.wg.Wait()
	close(w.results)
}
