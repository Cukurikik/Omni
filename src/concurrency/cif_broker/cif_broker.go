package cifbroker

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

// OMNI Engine: CIF Broker
// High throughput stream buffer for continuous isolation forest geometries.
type CifStreamBroker struct {
	maxIngestBuffer int
	currentBuffer   int
	mu              sync.Mutex
}

func NewCifStreamBroker(maxBuffer int) *CifStreamBroker {
	return &CifStreamBroker{
		maxIngestBuffer: maxBuffer,
		currentBuffer:   0,
	}
}

// Evaluate spatial ingestion constraints before tree computation
func (c *CifStreamBroker) ValidateIngestStream(packetSizePixels int) Result[bool] {
	c.mu.Lock()
	defer c.mu.Unlock()

	if packetSizePixels <= 0 {
		return Err[bool]("Topology violation: packet mass cannot be mathematically zero or negative")
	}

	if c.currentBuffer+packetSizePixels > c.maxIngestBuffer {
		return Err[bool]("Stream Overflow: geometric limits of concurrent CIF ingestion breached")
	}

	c.currentBuffer += packetSizePixels
	return Ok(true)
}

func (c *CifStreamBroker) FlashBufferLayer(packetSizePixels int) Result[int] {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.currentBuffer-packetSizePixels < 0 {
		return Err[int]("Buffer Underflow: mathematical state impossible (negative buffer)")
	}

	c.currentBuffer -= packetSizePixels
	return Ok(c.currentBuffer)
}
