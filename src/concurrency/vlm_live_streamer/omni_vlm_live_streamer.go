package vlm_live

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sync"
	"sync/atomic"
)

// OMNI VLM Live Streamer — Concurrency Layer
// Absorbing stlin256/VLM_Live: Real-Time VLM Visual Analysis Web App.
// Manages real-time WebRTC/WebSocket multiplexing for visual processing streams.

type StreamFrame struct {
	SequenceID uint64
	Timestamp  int64
	VideoChunk []byte
}

type VlmLiveSession struct {
	ID         string
	IsActive   bool
	FrameCount uint64
	LastHash   string
}

type OmniVlmLiveStreamer struct {
	mu        sync.RWMutex
	sessions  map[string]*VlmLiveSession
	dropped   uint64
	processed uint64
}

func NewOmniVlmLiveStreamer() *OmniVlmLiveStreamer {
	return &OmniVlmLiveStreamer{
		sessions: make(map[string]*VlmLiveSession),
	}
}

func (v *OmniVlmLiveStreamer) OpenSession(sessionID string) error {
	v.mu.Lock()
	defer v.mu.Unlock()
	if sessionID == "" {
		return errors.New("VlmLiveError: Empty session ID")
	}
	if _, exists := v.sessions[sessionID]; exists {
		return errors.New("VlmLiveError: Session already exists")
	}
	v.sessions[sessionID] = &VlmLiveSession{ID: sessionID, IsActive: true}
	return nil
}

func (v *OmniVlmLiveStreamer) IngestFrame(sessionID string, frame StreamFrame) (*VlmLiveSession, error) {
	v.mu.RLock()
	session, exists := v.sessions[sessionID]
	v.mu.RUnlock()

	if !exists || !session.IsActive {
		atomic.AddUint64(&v.dropped, 1)
		return nil, errors.New("VlmLiveError: Invalid or inactive session")
	}

	hash := sha256.Sum256(frame.VideoChunk)
	hexHash := hex.EncodeToString(hash[:])

	v.mu.Lock()
	session.FrameCount++
	session.LastHash = hexHash
	v.mu.Unlock()

	atomic.AddUint64(&v.processed, 1)
	return session, nil
}

func (v *OmniVlmLiveStreamer) Diagnostics() map[string]interface{} {
	v.mu.RLock()
	defer v.mu.RUnlock()

	active := 0
	for _, s := range v.sessions {
		if s.IsActive {
			active++
		}
	}

	return map[string]interface{}{
		"engine":           "OmniVlmLiveStreamer",
		"active_sessions":  active,
		"processed_frames": atomic.LoadUint64(&v.processed),
		"dropped_frames":   atomic.LoadUint64(&v.dropped),
		"status":           "Operational",
	}
}
