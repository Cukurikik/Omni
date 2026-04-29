package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type EvalJob struct {
	ModelID string
	Metrics []float64
}

type EvalRunner struct {
	jobs    chan EvalJob
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewEvalRunner(workers int) *EvalRunner {
	r := &EvalRunner{
		jobs:    make(chan EvalJob, 100),
		results: make(chan OmniResult, 100),
	}
	for i := 0; i < workers; i++ {
		r.wg.Add(1)
		go r.worker()
	}
	return r
}

func (r *EvalRunner) worker() {
	defer r.wg.Done()
	for job := range r.jobs {
		if len(job.Metrics) == 0 {
			r.results <- OmniResult{Error: fmt.Errorf("no metrics provided for %s", job.ModelID)}
			continue
		}
		
		// Calculate simple mean
		sum := 0.0
		for _, v := range job.Metrics {
			sum += v
		}
		mean := sum / float64(len(job.Metrics))
		
		r.results <- OmniResult{Value: fmt.Sprintf("Model %s evaluated. Mean Accuracy: %.4f", job.ModelID, mean)}
	}
}

func (r *EvalRunner) Submit(job EvalJob) {
	r.jobs <- job
}

func (r *EvalRunner) Close() {
	close(r.jobs)
	r.wg.Wait()
	close(r.results)
}
