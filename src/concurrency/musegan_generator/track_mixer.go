package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type TrackChunk struct {
	InstrumentID int
	Notes        []int // Pitches
}

type TrackMixer struct {
	trackBuffer chan TrackChunk
	wg          sync.WaitGroup
	mu          sync.Mutex
	masterMix   [][]int // Simulated multi-track matrix
}

func NewTrackMixer(numTracks int) *TrackMixer {
	return &TrackMixer{
		trackBuffer: make(chan TrackChunk, numTracks*10),
		masterMix:   make([][]int, numTracks),
	}
}

func (m *TrackMixer) Start(numMixers int) {
	for i := 0; i < numMixers; i++ {
		m.wg.Add(1)
		go m.mixLoop(i)
	}
}

func (m *TrackMixer) SubmitTrack(chunk TrackChunk) OmniResult {
	if chunk.InstrumentID < 0 || chunk.InstrumentID >= len(m.masterMix) {
		return OmniResult{Error: fmt.Errorf("invalid instrument ID")}
	}

	select {
	case m.trackBuffer <- chunk:
		return OmniResult{Value: "Track chunk accepted"}
	default:
		return OmniResult{Error: fmt.Errorf("mixer buffer full")}
	}
}

func (m *TrackMixer) mixLoop(mixerID int) {
	defer m.wg.Done()

	for chunk := range m.trackBuffer {
		m.mu.Lock()
		// Deterministically append notes to the master mix for the given instrument
		m.masterMix[chunk.InstrumentID] = append(m.masterMix[chunk.InstrumentID], chunk.Notes...)
		m.mu.Unlock()
	}
}

func (m *TrackMixer) StopAndGetMix() [][]int {
	close(m.trackBuffer)
	m.wg.Wait()
	return m.masterMix
}
