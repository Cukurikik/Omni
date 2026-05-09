package audiogen

import (
	"errors"
	"sync"
	"time"
)

type MidiNote struct {
	Pitch    int
	Velocity int
	StartMs  int
	Duration int
}

type MidiTrack struct {
	TrackName string
	Notes     []MidiNote
}

type OmniResult struct {
	Tracks []MidiTrack
	Error  error
}

type MidiParserPool struct {
	workers int
}

func NewMidiParserPool(workers int) *MidiParserPool {
	return &MidiParserPool{workers: workers}
}

// Concurrently parses a slice of raw MIDI byte buffers
func (p *MidiParserPool) ParseBatch(midiBuffers [][]byte) OmniResult {
	if len(midiBuffers) == 0 {
		return OmniResult{Error: errors.New("empty midi buffers")}
	}

	results := make([]MidiTrack, len(midiBuffers))
	errChan := make(chan error, len(midiBuffers))

	var wg sync.WaitGroup
	semaphore := make(chan struct{}, p.workers)

	for i, buffer := range midiBuffers {
		wg.Add(1)
		go func(idx int, buf []byte) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			if len(buf) == 0 {
				errChan <- errors.New("empty buffer encountered")
				return
			}

			// Simulating CPU bound binary parsing
			time.Sleep(15 * time.Millisecond)

			// Mock structural extraction
			track := MidiTrack{
				TrackName: "Generated_Track",
				Notes: []MidiNote{
					{Pitch: 60, Velocity: 100, StartMs: 0, Duration: 500},
					{Pitch: 64, Velocity: 80, StartMs: 500, Duration: 500},
					{Pitch: 67, Velocity: 90, StartMs: 1000, Duration: 1000},
				},
			}

			results[idx] = track

		}(i, buffer)
	}

	wg.Wait()
	close(errChan)

	for err := range errChan {
		if err != nil {
			return OmniResult{Error: err}
		}
	}

	return OmniResult{Tracks: results, Error: nil}
}
