// OMNI Concurrency Layer: valle_streamer.go
// Streams PCM chunks for VALL-E zero-shot TTS over HTTP chunked transfer.
// Bounds: 4KB chunk size to optimize network MTU

package network

import (
	"io"
)

const CHUNK_SIZE_BYTES = 4096

type OmniAudioError struct {
	Code    int
	Message string
}

type OmniAudioResult struct {
	BytesWritten int
	Error        *OmniAudioError
}

type ValleStreamer struct {
	writer io.Writer
}

func NewValleStreamer(w io.Writer) *ValleStreamer {
	return &ValleStreamer{writer: w}
}

// StreamPCM writes fixed bounded chunks of PCM data
func (s *ValleStreamer) StreamPCM(pcmData []byte) OmniAudioResult {
	if len(pcmData) == 0 {
		return OmniAudioResult{
			BytesWritten: 0,
			Error:        nil,
		}
	}

	totalWritten := 0

	for totalWritten < len(pcmData) {
		end := totalWritten + CHUNK_SIZE_BYTES
		if end > len(pcmData) {
			end = len(pcmData)
		}

		chunk := pcmData[totalWritten:end]
		n, err := s.writer.Write(chunk)

		if err != nil {
			return OmniAudioResult{
				BytesWritten: totalWritten,
				Error: &OmniAudioError{
					Code:    1,
					Message: "Network write failure on PCM chunk stream",
				},
			}
		}

		totalWritten += n
	}

	return OmniAudioResult{
		BytesWritten: totalWritten,
		Error:        nil,
	}
}
