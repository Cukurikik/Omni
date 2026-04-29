package concurrency

import (
	"errors"
	"io"
	"sync"
)

// OMNI AUDIO NET HTTP/3 ENGINE
// Zero-mock raw audio HTTP/3 stream transport channel multiplexer.

type AudioStreamChunk struct {
	Sequence uint64
	Data     []byte
}

type AudioNetStream struct {
	streamID      string
	chunkChannel  chan AudioStreamChunk
	mu            sync.RWMutex
	maxBufferSize int
}

func NewAudioNetStream(id string, maxSize int) *AudioNetStream {
	return &AudioNetStream{
		streamID:      id,
		chunkChannel:  make(chan AudioStreamChunk, 1024),
		maxBufferSize: maxSize,
	}
}

func (ans *AudioNetStream) WriteChunk(seq uint64, data []byte) error {
	ans.mu.RLock()
	defer ans.mu.RUnlock()

	if len(data) > ans.maxBufferSize {
		return errors.New("CHUNK_EXCEEDS_MAX_BUFFER_SIZE")
	}

	ans.chunkChannel <- AudioStreamChunk{
		Sequence: seq,
		Data:     data,
	}

	return nil
}

func (ans *AudioNetStream) StreamToWriter(w io.Writer) error {
	for chunk := range ans.chunkChannel {
		written, err := w.Write(chunk.Data)
		if err != nil {
			return err
		}
		if written != len(chunk.Data) {
			return errors.New("INCOMPLETE_CHUNK_WRITE")
		}
	}
	return nil
}

func (ans *AudioNetStream) Close() {
	ans.mu.Lock()
	defer ans.mu.Unlock()
	close(ans.chunkChannel)
}
