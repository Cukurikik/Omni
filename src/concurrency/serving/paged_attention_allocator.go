package serving

import (
	"errors"
)

// OMNI MOTHER SYSTEM - CONCURRENCY LAYER
// vLLM-Inspired PagedAttention Memory Allocator
var (
	ErrNoFreePages = errors.New("OMNI_FATAL: No")
)
