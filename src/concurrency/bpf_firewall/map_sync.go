package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type BpfMapEntry struct {
	Key   string
	Value uint32
}

type MapSynchronizer struct {
	updateQueue chan BpfMapEntry
	wg          sync.WaitGroup
}

func NewMapSynchronizer() *MapSynchronizer {
	s := &MapSynchronizer{
		updateQueue: make(chan BpfMapEntry, 100),
	}

	s.wg.Add(1)
	go s.syncLoop()

	return s
}

func (s *MapSynchronizer) syncLoop() {
	defer s.wg.Done()

	for entry := range s.updateQueue {
		// Simulate userspace-to-kernel eBPF map sync overhead
		time.Sleep(1 * time.Millisecond)
		if entry.Value > 0 {
			// fmt.Printf("BPF Map Sync: Updated rule for %s\n", entry.Key)
		}
	}
}

func (s *MapSynchronizer) UpdateMap(entry BpfMapEntry) OmniResult {
	select {
	case s.updateQueue <- entry:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Map update queue full")}
	}
}

func (s *MapSynchronizer) Close() {
	close(s.updateQueue)
	s.wg.Wait()
}
