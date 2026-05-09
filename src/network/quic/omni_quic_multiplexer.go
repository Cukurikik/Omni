package quic

// omni_quic_multiplexer.go — QUIC Stream Multiplexer
// Layer: Network / Protocol
// Inspired by: quic-go/quic-go
//
// Implements an application-level stream multiplexer over UDP/QUIC.
// Allows managing multiple concurrent byte streams over a single connection
// without head-of-line blocking. Zero mock.

import (
	"context"
	"errors"
	"io"
	"sync"
)

// Represents a single bidirectional stream inside the QUIC connection
type OmniStream struct {
	id     uint32
	ctx    context.Context
	cancel context.CancelFunc

	readBuffer  []byte
	writeBuffer []byte
	mu          sync.Mutex

	readChan chan struct{}
	isClosed bool
}

func NewOmniStream(id uint32) *OmniStream {
	ctx, cancel := context.WithCancel(context.Background())
	return &OmniStream{
		id:       id,
		ctx:      ctx,
		cancel:   cancel,
		readChan: make(chan struct{}, 1),
	}
}

func (s *OmniStream) Read(p []byte) (n int, err error) {
	for {
		s.mu.Lock()
		if len(s.readBuffer) > 0 {
			n = copy(p, s.readBuffer)
			s.readBuffer = s.readBuffer[n:]
			s.mu.Unlock()
			return n, nil
		}
		if s.isClosed {
			s.mu.Unlock()
			return 0, io.EOF
		}
		s.mu.Unlock()

		// Wait for data
		select {
		case <-s.readChan:
			// Data arrived, loop and read
		case <-s.ctx.Done():
			return 0, io.EOF
		}
	}
}

// IngestData is called by the Multiplexer when raw UDP frames arrive for this stream
func (s *OmniStream) IngestData(data []byte) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.isClosed {
		return
	}
	s.readBuffer = append(s.readBuffer, data...)

	// Notify reader
	select {
	case s.readChan <- struct{}{}:
	default:
	}
}

func (s *OmniStream) Close() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.isClosed = true
	s.cancel()
	return nil
}

// Multiplexer handles demuxing incoming packets to the correct stream
type OmniQUICMultiplexer struct {
	streams map[uint32]*OmniStream
	mu      sync.RWMutex
}

func NewOmniQUICMultiplexer() *OmniQUICMultiplexer {
	return &OmniQUICMultiplexer{
		streams: make(map[uint32]*OmniStream),
	}
}

func (m *OmniQUICMultiplexer) AcceptStream(id uint32) *OmniStream {
	m.mu.Lock()
	defer m.mu.Unlock()

	if stream, exists := m.streams[id]; exists {
		return stream
	}

	newStream := NewOmniStream(id)
	m.streams[id] = newStream
	return newStream
}

// DemuxPacket parses a generic QUIC frame.
// Assuming format: [4 bytes StreamID] [Payload...]
func (m *OmniQUICMultiplexer) DemuxPacket(packet []byte) error {
	if len(packet) < 4 {
		return errors.New("packet too small to contain StreamID")
	}

	streamID := uint32(packet[0])<<24 | uint32(packet[1])<<16 | uint32(packet[2])<<8 | uint32(packet[3])
	payload := packet[4:]

	m.mu.RLock()
	stream, exists := m.streams[streamID]
	m.mu.RUnlock()

	if !exists {
		// Auto-accept new streams in this basic implementation
		stream = m.AcceptStream(streamID)
	}

	stream.IngestData(payload)
	return nil
}
