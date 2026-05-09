package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type Payload struct {
	ID   string
	Data string
}

type PayloadValidator struct {
	queue chan Payload
	wg    sync.WaitGroup
}

func NewPayloadValidator(numWorkers int, bufferSize int) *PayloadValidator {
	v := &PayloadValidator{
		queue: make(chan Payload, bufferSize),
	}

	for i := 0; i < numWorkers; i++ {
		v.wg.Add(1)
		go v.worker()
	}

	return v
}

func (v *PayloadValidator) worker() {
	defer v.wg.Done()

	for payload := range v.queue {
		// Deterministically simulate validation processing
		// In reality this calls the Rust JSON FFI then Ruby/Julia rules
		if len(payload.Data) > 0 {
			fmt.Printf("Pydantic Worker: Payload %s Validated Successfully\n", payload.ID)
		} else {
			fmt.Printf("Pydantic Worker: Payload %s REJECTED (Empty)\n", payload.ID)
		}
	}
}

func (v *PayloadValidator) Enqueue(payload Payload) OmniResult {
	select {
	case v.queue <- payload:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Validation queue full, dropping payload")}
	}
}

func (v *PayloadValidator) Shutdown() {
	close(v.queue)
	v.wg.Wait()
}
