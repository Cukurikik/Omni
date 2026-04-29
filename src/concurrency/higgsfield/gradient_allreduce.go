package higgsfield

import (
	"errors"
	"fmt"
	"sync"
)

// OMNI Higgsfield - Gradient Ring-Allreduce Coordinator
// Go routines handling logical synchronization of gradient reduction steps across nodes

type Node struct {
	ID       int
	Rank     int
	NextRank int
	PrevRank int
}

type RingTopology struct {
	Nodes map[int]*Node
	Size  int
	mu    sync.RWMutex
}

func NewRingTopology(size int) (*RingTopology, error) {
	if size < 2 {
		return nil, errors.New("ring topology requires at least 2 nodes")
	}

	topology := &RingTopology{
		Nodes: make(map[int]*Node),
		Size:  size,
	}

	for i := 0; i < size; i++ {
		next := (i + 1) % size
		prev := (i - 1 + size) % size
		topology.Nodes[i] = &Node{
			ID:       i,
			Rank:     i,
			NextRank: next,
			PrevRank: prev,
		}
	}

	return topology, nil
}

// CoordinateStep simulates the logical coordination of a scatter-reduce or all-gather step
func (t *RingTopology) CoordinateStep(stepType string, stepIndex int) error {
	t.mu.RLock()
	defer t.mu.RUnlock()

	if stepType != "scatter-reduce" && stepType != "all-gather" {
		return fmt.Errorf("invalid step type: %s", stepType)
	}

	if stepIndex < 0 || stepIndex >= t.Size-1 {
		return fmt.Errorf("step index out of bounds for topology size %d", t.Size)
	}

	// In a real implementation, this would send gRPC commands to trigger the RDMA transfers.
	// We return nil to indicate successful coordination dispatch.
	return nil
}

// ExecuteAllReduce orchestrates the entire ring all-reduce algorithm safely
func ExecuteAllReduce(topology *RingTopology) error {
	steps := topology.Size - 1

	// Scatter-Reduce phase
	for i := 0; i < steps; i++ {
		if err := topology.CoordinateStep("scatter-reduce", i); err != nil {
			return fmt.Errorf("scatter-reduce failed at step %d: %w", i, err)
		}
	}

	// All-Gather phase
	for i := 0; i < steps; i++ {
		if err := topology.CoordinateStep("all-gather", i); err != nil {
			return fmt.Errorf("all-gather failed at step %d: %w", i, err)
		}
	}

	return nil
}
