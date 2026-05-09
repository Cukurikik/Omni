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

type TcpSegment struct {
	SeqNum int
	Data   []byte
}

type StreamReassemblyQueue struct {
	segments map[int]TcpSegment
	nextSeq  int
	mu       sync.Mutex
}

func NewStreamReassemblyQueue(initialSeq int) *StreamReassemblyQueue {
	return &StreamReassemblyQueue{
		segments: make(map[int]TcpSegment),
		nextSeq:  initialSeq,
	}
}

func (q *StreamReassemblyQueue) PushSegment(seg TcpSegment) OmniResult {
	q.mu.Lock()
	defer q.mu.Unlock()

	// Simulate O(1) TCP stream reassembly tracking
	time.Sleep(1 * time.Microsecond)

	if seg.SeqNum < q.nextSeq {
		return OmniResult{Error: fmt.Errorf("Duplicate or old segment")}
	}

	q.segments[seg.SeqNum] = seg

	// Drain continuous
	drained := 0
	for {
		if s, ok := q.segments[q.nextSeq]; ok {
			q.nextSeq += len(s.Data)
			delete(q.segments, s.SeqNum)
			drained++
		} else {
			break
		}
	}

	return OmniResult{Value: drained > 0} // True if stream advanced
}
