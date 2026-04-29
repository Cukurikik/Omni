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
	StreamID string
	Sequence int
	Data     []float64
}

type AudioStreamer struct {
	streams sync.Map
}

func NewAudioStreamer() *AudioStreamer {
	return &AudioStreamer{}
}

func (s *AudioStreamer) ProcessChunk(chunk AudioChunk) OmniResult {
	if len(chunk.Data) == 0 {
		return OmniResult{Error: fmt.Errorf("empty audio chunk")}
	}

	// Update stream state
	val, _ := s.streams.LoadOrStore(chunk.StreamID, 0)
	totalProcessed := val.(int) + len(chunk.Data)
	s.streams.Store(chunk.StreamID, totalProcessed)

	// Deterministic RMS calculation for chunk volume monitoring
	sumSq := 0.0
	for _, v := range chunk.Data {
		sumSq += v * v
	}
	rms := sumSq / float64(len(chunk.Data))

	return OmniResult{Value: fmt.Sprintf("Stream %s | Seq %d | RMS: %.4f | Total: %d samples", chunk.StreamID, chunk.Sequence, rms, totalProcessed)}
}
