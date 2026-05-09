package streaming

// omni_hls_muxer.go — HLS Video Muxer
// Layer: Network / Go
//
// Implements an HTTP Live Streaming (HLS) playlist generator and segment
// tracker for the OMNI media cluster. Strictly functional, zero mock.

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

type HLSSegment struct {
	URI       string
	Duration  float64
	Timestamp time.Time
}

type OmniHLSMuxer struct {
	playlistName   string
	targetDuration int
	segments       []HLSSegment
	sequenceNo     int
	windowSize     int // Number of segments to keep in the live playlist
	mu             sync.RWMutex
}

func NewOmniHLSMuxer(name string, targetDur int, windowSize int) *OmniHLSMuxer {
	return &OmniHLSMuxer{
		playlistName:   name,
		targetDuration: targetDur,
		segments:       make([]HLSSegment, 0),
		sequenceNo:     0,
		windowSize:     windowSize,
	}
}

// AddSegment appends a new chunk to the live stream playlist.
func (m *OmniHLSMuxer) AddSegment(uri string, duration float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	seg := HLSSegment{
		URI:       uri,
		Duration:  duration,
		Timestamp: time.Now(),
	}

	m.segments = append(m.segments, seg)

	// Maintain live window size
	if len(m.segments) > m.windowSize {
		m.segments = m.segments[1:]
		m.sequenceNo++
	}
}

// GenerateManifest creates the exact m3u8 string for client players.
func (m *OmniHLSMuxer) GenerateManifest() string {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var builder strings.Builder

	// M3U8 Header
	builder.WriteString("#EXTM3U\n")
	builder.WriteString("#EXT-X-VERSION:3\n")
	builder.WriteString(fmt.Sprintf("#EXT-X-TARGETDURATION:%d\n", m.targetDuration))
	builder.WriteString(fmt.Sprintf("#EXT-X-MEDIA-SEQUENCE:%d\n", m.sequenceNo))

	// Segments
	for _, seg := range m.segments {
		builder.WriteString(fmt.Sprintf("#EXTINF:%.3f,\n", seg.Duration))
		builder.WriteString(seg.URI + "\n")
	}

	return builder.String()
}

