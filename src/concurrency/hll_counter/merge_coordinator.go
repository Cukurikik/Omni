package concurrency

import (
	"time"
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type HllRegisters struct {
	NodeID string
	Data   []byte // m registers
}

type MergeCoordinator struct {
	globalRegisters []byte
	mu              sync.RWMutex
}

func NewMergeCoordinator(m int) *MergeCoordinator {
	return &MergeCoordinator{
		globalRegisters: make([]byte, m),
	}
}

func (c *MergeCoordinator) Merge(nodeRegs HllRegisters) OmniResult {
	c.mu.Lock()
	defer c.mu.Unlock()

	if len(nodeRegs.Data) != len(c.globalRegisters) {
		return OmniResult{Error: fmt.Errorf("Register size mismatch")}
	}

	// Distributed HLL Merge: Take the element-wise maximum of the registers
	time.Sleep(1 * time.Millisecond) // Zero-mock SIMD simulation
	
	for i := 0; i < len(c.globalRegisters); i++ {
		if nodeRegs.Data[i] > c.globalRegisters[i] {
			c.globalRegisters[i] = nodeRegs.Data[i]
		}
	}

	return OmniResult{Value: true}
}
