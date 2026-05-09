package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type AudioChunk struct {
	SequenceID int
	Data       []float64
}

type AudioBuffer struct {
	chunks []AudioChunk
	mu     sync.Mutex
	cond   *sync.Cond
}

func NewAudioBuffer() *AudioBuffer {
	b := &AudioBuffer{}
	b.cond = sync.NewCond(&b.mu)
	return b
}

func (b *AudioBuffer) WriteChunk(chunk AudioChunk) OmniResult {
	if len(chunk.Data) == 0 {
		return OmniResult{Error: fmt.Errorf("empty chunk provided")}
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	b.chunks = append(b.chunks, chunk)

	// Deterministic sorting to ensure in-order playback sequence
	for i := len(b.chunks) - 1; i > 0; i-- {
		if b.chunks[i].SequenceID < b.chunks[i-1].SequenceID {
			b.chunks[i], b.chunks[i-1] = b.chunks[i-1], b.chunks[i]
		}
	}

	b.cond.Signal()
	return OmniResult{Value: fmt.Sprintf("Chunk %d buffered", chunk.SequenceID)}
}

func (b *AudioBuffer) ReadNext() OmniResult {
	b.mu.Lock()
	defer b.mu.Unlock()

	for len(b.chunks) == 0 {
		b.cond.Wait()
	}

	chunk := b.chunks[0]
	b.chunks = b.chunks[1:]

	return OmniResult{Value: chunk}
}
