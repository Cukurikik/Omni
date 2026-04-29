package openstorypp

import (
	"errors"
	"sync"
)

// OMNI Result Monad Implementation
type Result[T any] struct {
	Value T
	Error error
}

func Ok[T any](val T) Result[T] {
	return Result[T]{Value: val, Error: nil}
}

func Err[T any](err string) Result[T] {
	return Result[T]{Error: errors.New(err)}
}

// OMNI Engine: OpenStoryPP Broker
// Concurrent structural narrative stream processor limiting topological cascade via goroutines.
type OpenStoryBroker struct {
	maxThreadCascade int
	mu               sync.Mutex
	activeCascades   int
}

func NewOpenStoryBroker(maxCascade int) *OpenStoryBroker {
	return &OpenStoryBroker{
		maxThreadCascade: maxCascade,
		activeCascades:   0,
	}
}

// Determines if a generative storyline token branch can spawn without CPU exhaustion
func (b *OpenStoryBroker) TryAcquireCascadeToken(storyDepth int) Result[bool] {
	b.mu.Lock()
	defer b.mu.Unlock()

	if storyDepth <= 0 {
		return Err[bool]("Mathematical boundary error: storyline topological depth must be positive")
	}

	if storyDepth > 100 {
		return Err[bool]("Topological boundary: Narrative depth mathematically exceeds causal constraints")
	}

	if b.activeCascades >= b.maxThreadCascade {
		return Err[bool]("Concurrency Exhaustion: Max storyline permutation branches reached")
	}

	b.activeCascades++
	return Ok(true)
}

func (b *OpenStoryBroker) ReleaseCascadeToken() Result[int] {
	b.mu.Lock()
	defer b.mu.Unlock()

	if b.activeCascades <= 0 {
		return Err[int]("Critical State Mismatch: cannot release unallocated zero-token")
	}

	b.activeCascades--
	return Ok(b.activeCascades)
}
