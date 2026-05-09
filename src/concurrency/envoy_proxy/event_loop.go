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

type ProxyRequest struct {
	ReqID    string
	TargetIP string
	Payload  int
}

type EventLoop struct {
	reqQueue chan ProxyRequest
	wg       sync.WaitGroup
}

func NewEventLoop(bufferSize int) *EventLoop {
	e := &EventLoop{
		reqQueue: make(chan ProxyRequest, bufferSize),
	}

	// Single threaded event loop multiplexer (like Node/Envoy libevent)
	e.wg.Add(1)
	go e.loop()

	return e
}

func (e *EventLoop) loop() {
	defer e.wg.Done()

	for req := range e.reqQueue {
		// Deterministic async I/O simulation
		time.Sleep(1 * time.Millisecond) // micro-sleep mimicking epoll wait
		fmt.Printf("Envoy EventLoop: Proxied %d bytes to %s [Req: %s]\n", req.Payload, req.TargetIP, req.ReqID)
	}
}

func (e *EventLoop) Proxy(req ProxyRequest) OmniResult {
	select {
	case e.reqQueue <- req:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Envoy 503: Event Loop saturated (Backpressure applied)")}
	}
}

func (e *EventLoop) Shutdown() {
	close(e.reqQueue)
	e.wg.Wait()
}
