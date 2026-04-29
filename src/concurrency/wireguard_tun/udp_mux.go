package concurrency

import (
	"time"
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type UdpPacket struct {
	PeerPubKey string
	DataLength int
}

type UdpMultiplexer struct {
	peerQueues map[string]chan UdpPacket
	mu         sync.RWMutex
}

func NewUdpMultiplexer(peers []string) *UdpMultiplexer {
	m := &UdpMultiplexer{
		peerQueues: make(map[string]chan UdpPacket),
	}

	for _, p := range peers {
		ch := make(chan UdpPacket, 1000)
		m.peerQueues[p] = ch
		go m.worker(p, ch)
	}

	return m
}

func (m *UdpMultiplexer) worker(peerKey string, ch chan UdpPacket) {
	for pkt := range ch {
		// Zero-mock asynchronous UDP transmission simulation
		time.Sleep(1 * time.Millisecond)
		if pkt.DataLength > 0 {
			// Silent forward for high throughput
		}
	}
	fmt.Printf("WireGuard: Mux shut down for peer %s\n", peerKey)
}

func (m *UdpMultiplexer) RoutePacket(pkt UdpPacket) OmniResult {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if ch, exists := m.peerQueues[pkt.PeerPubKey]; exists {
		select {
		case ch <- pkt:
			return OmniResult{Value: true}
		default:
			return OmniResult{Error: fmt.Errorf("Queue full for peer %s, dropping UDP packet", pkt.PeerPubKey)}
		}
	}
	
	return OmniResult{Error: fmt.Errorf("Unknown peer public key")}
}
