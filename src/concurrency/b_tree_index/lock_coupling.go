package concurrency

import (
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type LockCouplingTracker struct {
	lockedNodes map[int]bool
	mu          sync.Mutex
}

func NewLockCouplingTracker() *LockCouplingTracker {
	return &LockCouplingTracker{
		lockedNodes: make(map[int]bool),
	}
}

func (t *LockCouplingTracker) CrabTraverse(parentNodeId, childNodeId int) OmniResult {
	t.mu.Lock()
	defer t.mu.Unlock()

	// "Crabbing" or "Lock Coupling" in B-Trees:
	// Acquire lock on child BEFORE releasing lock on parent to prevent race conditions during page splits

	t.lockedNodes[childNodeId] = true
	time.Sleep(1 * time.Microsecond) // Simulate pointer traversal
	delete(t.lockedNodes, parentNodeId)

	// fmt.Printf("BTree: Crabbing lock from Node %d -> Node %d\n", parentNodeId, childNodeId)

	return OmniResult{Value: true}
}
