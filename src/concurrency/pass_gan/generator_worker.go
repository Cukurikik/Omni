package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type GeneratorWorker struct {
	taskQueue   chan int
	resultQueue chan string
	wg          sync.WaitGroup
}

func NewGeneratorWorker(bufferSize int) *GeneratorWorker {
	return &GeneratorWorker{
		taskQueue:   make(chan int, bufferSize),
		resultQueue: make(chan string, bufferSize),
	}
}

func (w *GeneratorWorker) Start(workers int) {
	for i := 0; i < workers; i++ {
		w.wg.Add(1)
		go w.generateLoop(i)
	}
}

func (w *GeneratorWorker) RequestPasswords(count int) OmniResult {
	if count <= 0 {
		return OmniResult{Error: fmt.Errorf("count must be positive")}
	}

	for i := 0; i < count; i++ {
		w.taskQueue <- i
	}
	return OmniResult{Value: "Requests queued"}
}

func (w *GeneratorWorker) generateLoop(workerID int) {
	defer w.wg.Done()

	// Deterministic character mapping based on seed offset
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"

	for taskID := range w.taskQueue {
		// Mathematical deterministic password generation simulation
		length := 8 + (taskID % 8) // Range 8 to 15
		result := make([]byte, length)

		for i := 0; i < length; i++ {
			// Deterministic pseudo-random index
			idx := (workerID*31 + taskID*17 + i*7) % len(charset)
			result[i] = charset[idx]
		}

		w.resultQueue <- string(result)
	}
}

func (w *GeneratorWorker) Stop() {
	close(w.taskQueue)
	w.wg.Wait()
	close(w.resultQueue)
}
