package network_moe

import (
	"sync"
	"time"
)

// OMNI MOTHER Production Zero-Mock BBR Congestion Control
// Bottleneck Bandwidth and Round-trip propagation time logic applied at the
// application layer for MoE gRPC stream pacing.

type BBRState int

const (
	Startup BBRState = iota
	Drain
	ProbeBW
	ProbeRTT
)

type OmniBBR struct {
	mu         sync.Mutex
	state      BBRState
	minRTT     time.Duration
	maxBW      float64 // bytes per second
	pacingRate float64
	cwnd       int // congestion window

	roundCount int
}

func NewOmniBBR() *OmniBBR {
	return &OmniBBR{
		state:      Startup,
		minRTT:     1 * time.Hour, // infinity
		maxBW:      0,
		pacingRate: 1024 * 1024, // 1 MB/s init
		cwnd:       4 * 1024,    // 4 KB init
	}
}

func (b *OmniBBR) OnAck(bytesDelivered int, rtt time.Duration) {
	b.mu.Lock()
	defer b.mu.Unlock()

	// Update Min RTT
	if rtt > 0 && rtt < b.minRTT {
		b.minRTT = rtt
	}

	// Delivery Rate = bytes / RTT
	bw := float64(bytesDelivered) / rtt.Seconds()
	if bw > b.maxBW {
		b.maxBW = bw
	}

	// State Machine Transitions
	switch b.state {
	case Startup:
		// Double pacing rate every round until BW plateau
		b.pacingRate *= 2.0
		b.cwnd *= 2
		if b.pacingRate >= b.maxBW { // Simplified plateau check
			b.state = Drain
		}
	case Drain:
		b.pacingRate = b.maxBW * 0.5 // Drain queue
		b.state = ProbeBW
	case ProbeBW:
		b.pacingRate = b.maxBW * 1.25 // Probe for more BW
	}
}

func (b *OmniBBR) GetPacingRate() float64 {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.pacingRate
}

