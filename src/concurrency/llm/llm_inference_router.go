package llm

import (
	"errors"
	"sync"
	"sync/atomic"
)

type InferResult struct {
	IsOk  bool
	Error error
}
type InferenceRouter struct {
	active int32
	mu     sync.Mutex
}

func NewInferenceRouter() *InferenceRouter { return &InferenceRouter{} }
func (r *InferenceRouter) RouteRequest(modelId string, tokenCount int) InferResult {
	if modelId == "" {
		return InferResult{false, errors.New("empty model ID")}
	}
	if tokenCount > 131072 {
		return InferResult{false, errors.New("tokens exceed 128K")}
	}
	cur := atomic.AddInt32(&r.active, 1)
	if cur > 2000 {
		atomic.AddInt32(&r.active, -1)
		return InferResult{false, errors.New("concurrency limit")}
	}
	go func() { defer atomic.AddInt32(&r.active, -1) }()
	return InferResult{true, nil}
}
