package concurrency

import (
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type Frame struct {
	ID        int64
	Timestamp int64
	Data      []byte
}

type FrameRingBuffer struct {
	frames     []Frame
	head       int
	tail       int
	count      int
	capacity   int
	mu         sync.Mutex
	cond       *sync.Cond
}

func NewFrameRingBuffer(capacity int) *FrameRingBuffer {
	rb := &FrameRingBuffer{
		frames:   make([]Frame, capacity),
		capacity: capacity,
	}
	rb.cond = sync.NewCond(&rb.mu)
	return rb
}

func (rb *FrameRingBuffer) PushFrame(frame Frame) OmniResult {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	// Overwrite oldest if full (Ring Buffer nature)
	rb.frames[rb.head] = frame
	rb.head = (rb.head + 1) % rb.capacity

	if rb.count < rb.capacity {
		rb.count++
	} else {
		rb.tail = (rb.tail + 1) % rb.capacity // Push tail forward
	}

	rb.cond.Signal() // Notify consumers
	return OmniResult{Value: "Frame pushed"}
}

func (rb *FrameRingBuffer) PopLatestFrame() OmniResult {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	for rb.count == 0 {
		rb.cond.Wait()
	}

	// Always get the most recent frame, ignoring stale ones to minimize latency
	latestIdx := (rb.head - 1 + rb.capacity) % rb.capacity
	frame := rb.frames[latestIdx]

	// Drain buffer (we only care about the absolute latest)
	rb.count = 0
	rb.tail = rb.head

	return OmniResult{Value: frame}
}
