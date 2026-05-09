package network_gocore

import (
	"fmt"
	"sync"
)

// FoldTaskDistributor manages the distribution of protein sequences
// across the GPU cluster for folding inference.
type FoldTaskDistributor struct {
	mu       sync.Mutex
	TaskPool []string
	Workers  []string
}

func NewFoldTaskDistributor() *FoldTaskDistributor {
	return &FoldTaskDistributor{
		TaskPool: make([]string, 0),
		Workers:  make([]string, 0),
	}
}

func (d *FoldTaskDistributor) SubmitSequence(sequence string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.TaskPool = append(d.TaskPool, sequence)
}

func (d *FoldTaskDistributor) AssignNext(workerID string) (string, error) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if len(d.TaskPool) == 0 {
		return "", fmt.Errorf("no pending tasks")
	}

	seq := d.TaskPool[0]
	d.TaskPool = d.TaskPool[1:]
	return seq, nil
}

