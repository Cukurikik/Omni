package network_gocore

import (
	"errors"
	"sync"
)

type ChimeraNode struct {
	ID       string
	Stage    int
	IsActive bool
	mu       sync.Mutex
}

func NewChimeraNode(id string, stage int) *ChimeraNode {
	return &ChimeraNode{
		ID:       id,
		Stage:    stage,
		IsActive: true,
	}
}

func (n *ChimeraNode) ProcessMicrobatch(data []byte) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	if !n.IsActive {
		return errors.New("node is inactive")
	}

	// Zero mock processing simulation
	if len(data) == 0 {
		return errors.New("empty microbatch data")
	}

	return nil
}

