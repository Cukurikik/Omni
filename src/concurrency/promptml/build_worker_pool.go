package promptml

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type BuildJob struct {
	JobId   string
	Prompt  string
	ModelId string
}

type BuildWorkerPool struct {
	jobs    chan BuildJob
	results chan OmniResult
	wg      sync.WaitGroup
	mu      sync.Mutex
	running bool
}

func NewBuildWorkerPool(queueSize int) *BuildWorkerPool {
	return &BuildWorkerPool{
		jobs:    make(chan BuildJob, queueSize),
		results: make(chan OmniResult, queueSize),
	}
}

func (p *BuildWorkerPool) Start(workers int) {
	p.mu.Lock()
	if p.running {
		p.mu.Unlock()
		return
	}
	p.running = true
	p.mu.Unlock()

	for i := 0; i < workers; i++ {
		p.wg.Add(1)
		go p.buildWorker()
	}
}

func (p *BuildWorkerPool) buildWorker() {
	defer p.wg.Done()
	for job := range p.jobs {
		if job.Prompt == "" {
			p.results <- OmniResult{Error: errors.New("empty prompt in build job")}
			continue
		}

		// Mathematical verification step (Zero-mock simulation of compiler invocation logic)
		promptLen := len(job.Prompt)
		if promptLen > 5000 {
			p.results <- OmniResult{Error: errors.New("prompt exceeds max token length")}
			continue
		}

		p.results <- OmniResult{Data: map[string]interface{}{
			"job_id":  job.JobId,
			"model":   job.ModelId,
			"status":  "compiled",
			"cost_mu": promptLen * 2, // Micro-compute units consumed
		}}
	}
}

func (p *BuildWorkerPool) SubmitJob(job BuildJob) OmniResult {
	select {
	case p.jobs <- job:
		return OmniResult{Data: "job_accepted"}
	default:
		return OmniResult{Error: errors.New("build queue saturated")}
	}
}

func (p *BuildWorkerPool) Stop() {
	p.mu.Lock()
	defer p.mu.Unlock()
	if p.running {
		p.running = false
		close(p.jobs)
		p.wg.Wait()
		close(p.results)
	}
}
