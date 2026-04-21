// ===========================================================================
// OMNI STREAMING RELAY ENGINE (POLYLINGUAL REMEDIATION)
// ===========================================================================
// Absorbed From  : ossrs/srs + sonobus + nymphcast concepts
// Logic Inherited: Go / Network Layer (Goroutine Fan-Out Stream Relay)
// Domain Layer   : Network (Go Core)
// ===========================================================================
//
// By studying SRS Media Server and Sonobus, Mother learned that live
// streaming relay is fundamentally a fan-out pattern: one ingest goroutine
// receives data, then broadcasts it to N subscriber goroutines via channels.
// Go's CSP model (channels + goroutines) maps perfectly to this architecture,
// providing built-in backpressure (buffered channels) and graceful shutdown
// (context cancellation) without any external dependencies.

package omni_streaming_relay

import (
	"context"
	"fmt"
	"math"
	"sync"
	"time"
)

// StreamConfig holds relay configuration.
type StreamConfig struct {
	BufferSize     int           // Channel buffer depth per subscriber
	MaxSubscribers int           // Hard cap on concurrent viewers
	IngestTimeout  time.Duration // Max time to wait for ingest data
	RelayID        string        // Unique relay identifier
}

// DefaultConfig returns sensible production defaults.
func DefaultConfig() StreamConfig {
	return StreamConfig{
		BufferSize:     256,
		MaxSubscribers: 1024,
		IngestTimeout:  30 * time.Second,
		RelayID:        "omni-relay-default",
	}
}

// StreamPacket represents one unit of streamed data (audio/video chunk).
type StreamPacket struct {
	SequenceNum uint64
	Timestamp   time.Time
	PayloadSize int
	Payload     []byte
	ContentType string // "audio/opus", "video/h264", etc.
}

// Subscriber represents a connected viewer/listener.
type Subscriber struct {
	ID       string
	Channel  chan StreamPacket
	JoinedAt time.Time
}

// RelayStats tracks real-time metrics.
type RelayStats struct {
	PacketsRelayed   uint64
	BytesRelayed     uint64
	SubscriberCount  int
	DroppedPackets   uint64
	PeakSubscribers  int
	UptimeSeconds    float64
}

// OmniStreamingRelayEngine is the core fan-out relay.
type OmniStreamingRelayEngine struct {
	config      StreamConfig
	subscribers map[string]*Subscriber
	mu          sync.RWMutex
	stats       RelayStats
	startTime   time.Time
	ctx         context.Context
	cancel      context.CancelFunc
	ingestCh    chan StreamPacket
	seqCounter  uint64
}

// NewOmniStreamingRelayEngine creates a new relay engine.
func NewOmniStreamingRelayEngine(cfg StreamConfig) *OmniStreamingRelayEngine {
	ctx, cancel := context.WithCancel(context.Background())
	return &OmniStreamingRelayEngine{
		config:      cfg,
		subscribers: make(map[string]*Subscriber),
		startTime:   time.Now(),
		ctx:         ctx,
		cancel:      cancel,
		ingestCh:    make(chan StreamPacket, cfg.BufferSize),
	}
}

// Subscribe adds a new subscriber to the relay. Returns subscriber ID.
func (e *OmniStreamingRelayEngine) Subscribe(id string) (*Subscriber, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if len(e.subscribers) >= e.config.MaxSubscribers {
		return nil, fmt.Errorf("max subscribers (%d) reached", e.config.MaxSubscribers)
	}

	if _, exists := e.subscribers[id]; exists {
		return nil, fmt.Errorf("subscriber %s already exists", id)
	}

	sub := &Subscriber{
		ID:       id,
		Channel:  make(chan StreamPacket, e.config.BufferSize),
		JoinedAt: time.Now(),
	}
	e.subscribers[id] = sub
	e.stats.SubscriberCount = len(e.subscribers)

	if e.stats.SubscriberCount > e.stats.PeakSubscribers {
		e.stats.PeakSubscribers = e.stats.SubscriberCount
	}

	return sub, nil
}

// Unsubscribe removes a subscriber and closes their channel.
func (e *OmniStreamingRelayEngine) Unsubscribe(id string) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if sub, exists := e.subscribers[id]; exists {
		close(sub.Channel)
		delete(e.subscribers, id)
		e.stats.SubscriberCount = len(e.subscribers)
	}
}

// Ingest pushes a raw data packet into the relay for fan-out distribution.
func (e *OmniStreamingRelayEngine) Ingest(payload []byte, contentType string) {
	e.seqCounter++
	pkt := StreamPacket{
		SequenceNum: e.seqCounter,
		Timestamp:   time.Now(),
		PayloadSize: len(payload),
		Payload:     payload,
		ContentType: contentType,
	}

	// Non-blocking send to ingest channel
	select {
	case e.ingestCh <- pkt:
	default:
		// Ingest buffer full — drop oldest (backpressure)
		e.stats.DroppedPackets++
	}
}

// RunFanOut is the central relay loop. Reads from ingest and broadcasts
// to all subscribers. This MUST run in its own goroutine.
func (e *OmniStreamingRelayEngine) RunFanOut() {
	for {
		select {
		case <-e.ctx.Done():
			return
		case pkt := <-e.ingestCh:
			e.broadcast(pkt)
		}
	}
}

// broadcast sends a packet to every active subscriber.
// Uses non-blocking sends to prevent one slow consumer from blocking others.
func (e *OmniStreamingRelayEngine) broadcast(pkt StreamPacket) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	for _, sub := range e.subscribers {
		select {
		case sub.Channel <- pkt:
			// Successfully delivered
		default:
			// Subscriber's buffer full — drop for this subscriber
			e.stats.DroppedPackets++
		}
	}

	e.stats.PacketsRelayed++
	e.stats.BytesRelayed += uint64(pkt.PayloadSize)
}

// Shutdown gracefully stops the relay and closes all subscriber channels.
func (e *OmniStreamingRelayEngine) Shutdown() {
	e.cancel()

	e.mu.Lock()
	defer e.mu.Unlock()

	for id, sub := range e.subscribers {
		close(sub.Channel)
		delete(e.subscribers, id)
	}
}

// GetStats returns a snapshot of relay metrics.
func (e *OmniStreamingRelayEngine) GetStats() RelayStats {
	e.mu.RLock()
	defer e.mu.RUnlock()

	stats := e.stats
	stats.UptimeSeconds = math.Round(time.Since(e.startTime).Seconds()*100) / 100
	return stats
}

// Diagnostics returns structured health info for the OMNI Engine Registry.
func (e *OmniStreamingRelayEngine) Diagnostics() map[string]interface{} {
	stats := e.GetStats()
	return map[string]interface{}{
		"engine":            "OmniStreamingRelayEngine",
		"layer":             "Go Network",
		"relay_id":          e.config.RelayID,
		"subscribers":       stats.SubscriberCount,
		"peak_subscribers":  stats.PeakSubscribers,
		"packets_relayed":   stats.PacketsRelayed,
		"bytes_relayed":     stats.BytesRelayed,
		"dropped_packets":   stats.DroppedPackets,
		"uptime_seconds":    stats.UptimeSeconds,
		"buffer_size":       e.config.BufferSize,
		"max_subscribers":   e.config.MaxSubscribers,
		"learned_logic": []string{
			"goroutine-fan-out-broadcast",
			"non-blocking-channel-send",
			"context-cancellation-shutdown",
			"rw-mutex-subscriber-safety",
			"backpressure-via-buffered-channels",
		},
	}
}
