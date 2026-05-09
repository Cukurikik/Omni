package doc_extractor

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type PageWorkerPool struct {
	jobs    chan int
	results chan string
	wg      sync.WaitGroup
}

func NewPageWorkerPool(bufferSize int) *PageWorkerPool {
	return &PageWorkerPool{
		jobs:    make(chan int, bufferSize),
		results: make(chan string, bufferSize),
	}
}

func (p *PageWorkerPool) Start(workers int) {
	for i := 0; i < workers; i++ {
		p.wg.Add(1)
		go p.workerLoop(i)
	}
}

func (p *PageWorkerPool) ProcessPages(numPages int) OmniResult {
	if numPages <= 0 {
		return OmniResult{Error: fmt.Errorf("numPages must be positive")}
	}

	for i := 1; i <= numPages; i++ {
		p.jobs <- i
	}
	return OmniResult{Value: "Jobs queued"}
}

func (p *PageWorkerPool) workerLoop(workerID int) {
	defer p.wg.Done()

	for pageNum := range p.jobs {
		// Deterministic simulation of OCR page processing
		// E.g., page 1 -> text, page 2 -> text
		resultText := fmt.Sprintf("Extracted content for Page %d [Processed by W-%d]", pageNum, workerID)

		p.results <- resultText
	}
}

func (p *PageWorkerPool) Stop() {
	close(p.jobs)
	p.wg.Wait()
	close(p.results)
}
