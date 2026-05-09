package hermes_edge

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sync"
	"time"
)

// OMNI Hermes Edge Pipeline
// Absorbing maximyudayev/hermes for low-latency event ingestion and verification

type PayloadType uint8

const (
	TypeTelemetry PayloadType = iota
	TypeVision
	TypeDiagnostic
)

type EventPacket struct {
	Timestamp int64
	Type      PayloadType
	Data      []byte
	Signature string
}

type OmniHermesEdge struct {
	mu             sync.RWMutex
	eventStream    chan EventPacket
	processedBytes uint64
	active         bool
}

func NewOmniHermesEdge(bufferSize int) (*OmniHermesEdge, error) {
	if bufferSize <= 0 || bufferSize > 1000000 {
		return nil, errors.New("HermesError: Buffer size out of physical bounds")
	}
	return &OmniHermesEdge{
		eventStream: make(chan EventPacket, bufferSize),
		active:      true,
	}, nil
}

// IngestData accepts raw edge data, calculates a cryptographic SHA256 signature for integrity,
// and drops it into a non-blocking channel for high-throughput concurrency processing.
func (h *OmniHermesEdge) IngestData(dataType PayloadType, rawData []byte) (string, error) {
	h.mu.RLock()
	isActive := h.active
	h.mu.RUnlock()

	if !isActive {
		return "", errors.New("HermesError: Pipeline inactive")
	}

	if len(rawData) == 0 {
		return "", errors.New("HermesError: Empty payload rejected")
	}

	// Zero-mock mathematical cryptographic hashing for payload integrity
	hash := sha256.Sum256(rawData)
	signature := hex.EncodeToString(hash[:])

	packet := EventPacket{
		Timestamp: time.Now().UnixNano(),
		Type:      dataType,
		Data:      bytes.Clone(rawData), // Prevent memory corruption from caller
		Signature: signature,
	}

	// Non-blocking write to channel
	select {
	case h.eventStream <- packet:
		h.mu.Lock()
		h.processedBytes += uint64(len(rawData))
		h.mu.Unlock()
		return signature, nil
	default:
		return "", errors.New("HermesError: Pipeline congestion, packet dropped")
	}
}

func (h *OmniHermesEdge) Shutdown() {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.active = false
	close(h.eventStream)
}

func (h *OmniHermesEdge) Diagnostics() map[string]interface{} {
	h.mu.RLock()
	defer h.mu.RUnlock()
	return map[string]interface{}{
		"engine":          "OmniHermesEdge",
		"processed_bytes": h.processedBytes,
		"buffer_usage":    len(h.eventStream),
		"status":          h.active,
	}
}
