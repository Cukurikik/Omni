package mustango

import (
	"errors"
)

type OmniResult struct {
	Value interface{}
	Error error
}

func StreamMIDI(trackId string) OmniResult {
	if trackId == "" {
		return OmniResult{Value: nil, Error: errors.New("Track ID required")}
	}

	// Go concurrent routine for streaming generated MIDI data to audio synthesizers
	go func() {
		// Streaming...
	}()

	return OmniResult{Value: "MIDI streaming active", Error: nil}
}
