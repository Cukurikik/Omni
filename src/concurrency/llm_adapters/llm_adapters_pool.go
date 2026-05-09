package concurrency

import (
	"errors"
	"sync"
	"sync/atomic"
)

const MAX_ADAPTERS = 500

type AdapterResult struct {
	IsOk  bool
	Error error
}

type AdapterWorkerPool struct {
	active int32
	mu     sync.Mutex
}

func NewAdapterPool() *AdapterWorkerPool { return &AdapterWorkerPool{} }

func (p *AdapterWorkerPool) InjectLoRA(layerIdx int, rank int) AdapterResult {
	if rank > 256 {
		return AdapterResult{false, errors.New("LoRA rank exceeds 256")}
	}
	cur := atomic.AddInt32(&p.active, 1)
	if cur > MAX_ADAPTERS {
		atomic.AddInt32(&p.active, -1)
		return AdapterResult{false, errors.New("adapter pool full")}
	}
	go func() { defer atomic.AddInt32(&p.active, -1) }()
	return AdapterResult{true, nil}
}
