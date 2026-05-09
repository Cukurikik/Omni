package llm

import (
	"errors"
	"sync"
	"sync/atomic"
)

type BlenderResult struct {
	IsOk  bool
	Error error
}
type LLMBlenderRouter struct {
	active int32
	mu     sync.Mutex
}

func NewBlenderRouter() *LLMBlenderRouter { return &LLMBlenderRouter{} }
func (r *LLMBlenderRouter) DispatchToModel(modelIdx int, prompt string) BlenderResult {
	if modelIdx < 0 || modelIdx > 20 {
		return BlenderResult{false, errors.New("model index out of range [0,20]")}
	}
	if len(prompt) > 65536 {
		return BlenderResult{false, errors.New("prompt exceeds 64KB")}
	}
	cur := atomic.AddInt32(&r.active, 1)
	if cur > 1000 {
		atomic.AddInt32(&r.active, -1)
		return BlenderResult{false, errors.New("dispatch limit")}
	}
	go func() { defer atomic.AddInt32(&r.active, -1) }()
	return BlenderResult{true, nil}
}
