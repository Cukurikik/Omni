package concurrency

// CLoT humor generation worker pool.
// Go CSP channels for leap-of-thought routing.

import (
	"errors"
	"sync"
)

const MAX_CLOT_WORKERS = 128

type OmniResult struct {
	IsOk  bool
	Value interface{}
	Error error
}

type CLoTPool struct {
	tasks chan []byte
	wg    sync.WaitGroup
}

func NewCLoTPool() *CLoTPool {
	return &CLoTPool{
		tasks: make(chan []byte, 1000),
	}
}

func (p *CLoTPool) Dispatch(task []byte) OmniResult {
	if len(p.tasks) == cap(p.tasks) {
		return OmniResult{IsOk: false, Error: errors.New("CLoT humor pool exhausted")}
	}
	p.tasks <- task
	return OmniResult{IsOk: true}
}

func (p *CLoTPool) StartWorkers(count int) {
	if count > MAX_CLOT_WORKERS {
		count = MAX_CLOT_WORKERS
	}
	for i := 0; i < count; i++ {
		p.wg.Add(1)
		go func() {
			defer p.wg.Done()
			for _ = range p.tasks {
				// Process leap of thought
			}
		}()
	}
}
