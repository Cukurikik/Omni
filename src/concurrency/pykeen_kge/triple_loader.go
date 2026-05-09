package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type KGTriple struct {
	Head int
	Rel  int
	Tail int
}

type TripleLoader struct {
	batchQueue chan []KGTriple
	wg         sync.WaitGroup
	batchSize  int
}

func NewTripleLoader(bufferSize int, batchSize int) *TripleLoader {
	return &TripleLoader{
		batchQueue: make(chan []KGTriple, bufferSize),
		batchSize:  batchSize,
	}
}

func (l *TripleLoader) Start(workers int) {
	for i := 0; i < workers; i++ {
		l.wg.Add(1)
		go l.workerLoop(i)
	}
}

func (l *TripleLoader) EnqueueBatch(batch []KGTriple) OmniResult {
	if len(batch) != l.batchSize {
		return OmniResult{Error: fmt.Errorf("batch size mismatch")}
	}

	select {
	case l.batchQueue <- batch:
		return OmniResult{Value: "Batch enqueued"}
	default:
		return OmniResult{Error: fmt.Errorf("loader queue full")}
	}
}

func (l *TripleLoader) workerLoop(id int) {
	defer l.wg.Done()
	for batch := range l.batchQueue {
		// Deterministic batch preprocessing validation
		valid := true
		for _, t := range batch {
			if t.Head < 0 || t.Tail < 0 || t.Rel < 0 {
				valid = false
				break
			}
		}
		if valid {
			// Ready for model consumption
			_ = batch
		}
	}
}

func (l *TripleLoader) Stop() {
	close(l.batchQueue)
	l.wg.Wait()
}
