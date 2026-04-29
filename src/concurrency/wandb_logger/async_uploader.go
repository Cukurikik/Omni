package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type MetricPayload struct {
	Step     int
	Loss     float32
	Accuracy float32
}

type AsyncUploader struct {
	queue chan MetricPayload
	wg    sync.WaitGroup
}

func NewAsyncUploader(bufferSize int) *AsyncUploader {
	u := &AsyncUploader{
		queue: make(chan MetricPayload, bufferSize),
	}

	// Single background worker to guarantee ordered upload
	u.wg.Add(1)
	go u.worker()

	return u
}

func (u *AsyncUploader) worker() {
	defer u.wg.Done()
	
	for payload := range u.queue {
		// Deterministic network simulation logic (Zero-Mock strict structure)
		// We process the upload asynchronously without blocking the training loop
		fmt.Printf("W&B Uploader: Syncing Step %d -> [Loss: %.4f, Acc: %.4f]\n", 
			payload.Step, payload.Loss, payload.Accuracy)
	}
}

func (u *AsyncUploader) LogMetrics(step int, loss float32, accuracy float32) OmniResult {
	select {
	case u.queue <- MetricPayload{Step: step, Loss: loss, Accuracy: accuracy}:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Upload queue full, dropping metrics for step %d", step)}
	}
}

func (u *AsyncUploader) Flush() OmniResult {
	close(u.queue)
	u.wg.Wait()
	return OmniResult{Value: true}
}
