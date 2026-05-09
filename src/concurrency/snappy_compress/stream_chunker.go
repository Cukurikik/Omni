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

type StreamChunk struct {
	ChunkID int
	Size    int
}

type StreamCompressor struct {
	chunkQueue chan StreamChunk
	wg         sync.WaitGroup
}

func NewStreamCompressor(workers int) *StreamCompressor {
	c := &StreamCompressor{
		chunkQueue: make(chan StreamChunk, 200),
	}

	for i := 0; i < workers; i++ {
		c.wg.Add(1)
		go c.worker()
	}

	return c
}

func (c *StreamCompressor) worker() {
	defer c.wg.Done()

	for chunk := range c.chunkQueue {
		// Simulate fast compression overhead
		time.Sleep(2 * time.Millisecond)
		if chunk.Size > 0 {
			// fmt.Printf("Snappy Worker: Compressed chunk %d\n", chunk.ChunkID)
		}
	}
}

func (c *StreamCompressor) EnqueueChunk(chunk StreamChunk) OmniResult {
	select {
	case c.chunkQueue <- chunk:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Compression buffer full")}
	}
}
