package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type HandshakeEvent struct {
	ConnectionID string
	State        string
}

type HandshakePool struct {
	queue chan HandshakeEvent
	wg    sync.WaitGroup
}

func NewHandshakePool(workers int) *HandshakePool {
	p := &HandshakePool{
		queue: make(chan HandshakeEvent, 500),
	}

	for i := 0; i < workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}

	return p
}

func (p *HandshakePool) worker(id int) {
	defer p.wg.Done()

	for event := range p.queue {
		// Simulate cryptographic handshake processing time
		time.Sleep(15 * time.Millisecond)
		if event.State == "CLIENT_HELLO" {
			// fmt.Printf("TLS Worker [%d]: Processing Handshake for %s\n", id, event.ConnectionID)
		}
	}
}

func (p *HandshakePool) Dispatch(event HandshakeEvent) OmniResult {
	select {
	case p.queue <- event:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("TLS Handshake queue saturated, rejecting connection")}
	}
}
