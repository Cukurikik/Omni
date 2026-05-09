// @omni-domain Concurrency Layer (OpenTulpa)
// @omni-source Semester 12 Batch 37
// @omni-description OpenTulpa actor model for autonomous persona generation.
// @omni-requirement zero-mock, monadic-error

package opentulpa

import (
	"context"
	"errors"
	"sync"
	"time"
)

type OmniResult[T any] struct {
	Ok    bool
	Value T
	Err   error
}

type TulpaState string

const (
	StateDormant  TulpaState = "DORMANT"
	StateActive   TulpaState = "ACTIVE"
	StateLearning TulpaState = "LEARNING"
)

type TulpaActor struct {
	id         string
	state      TulpaState
	memoryPool []string
	mutex      sync.RWMutex
}

type TulpaOrchestrator struct {
	actors map[string]*TulpaActor
	mutex  sync.RWMutex
}

func NewOrchestrator() *TulpaOrchestrator {
	return &TulpaOrchestrator{
		actors: make(map[string]*TulpaActor),
	}
}

func (o *TulpaOrchestrator) SpawnTulpa(id string) OmniResult[*TulpaActor] {
	if id == "" {
		return OmniResult[*TulpaActor]{Ok: false, Err: errors.New("tulpa ID cannot be empty")}
	}

	o.mutex.Lock()
	defer o.mutex.Unlock()

	if _, exists := o.actors[id]; exists {
		return OmniResult[*TulpaActor]{Ok: false, Err: errors.New("tulpa already exists")}
	}

	actor := &TulpaActor{
		id:         id,
		state:      StateDormant,
		memoryPool: make([]string, 0),
	}

	o.actors[id] = actor
	return OmniResult[*TulpaActor]{Ok: true, Value: actor}
}

func (t *TulpaActor) IngestMemory(ctx context.Context, memory string) OmniResult[bool] {
	t.mutex.Lock()
	defer t.mutex.Unlock()

	select {
	case <-ctx.Done():
		return OmniResult[bool]{Ok: false, Err: ctx.Err()}
	default:
		t.state = StateLearning
		time.Sleep(10 * time.Millisecond) // Simulate neural integration
		t.memoryPool = append(t.memoryPool, memory)
		t.state = StateActive
		return OmniResult[bool]{Ok: true, Value: true}
	}
}
