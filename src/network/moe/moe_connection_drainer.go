// moe_connection_drainer.go — Network / Orchestration
// Layer: Network / Infra — Graceful Connection Draining
//
// When deploying a new version of the Go API Gateway to Kubernetes, standard
// termination instantly kills all active user streams (SSE/gRPC). This module
// catches the SIGTERM signal and gracefully drains existing connections, preventing
// new ones while waiting for active streams to finish generating.

package network_moe

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type GracefulServer struct {
	httpServer     *http.Server
	activeStreams  sync.WaitGroup
	isShuttingDown bool
	mu             sync.RWMutex
}

func NewGracefulServer(addr string, handler http.Handler) *GracefulServer {
	return &GracefulServer{
		httpServer: &http.Server{
			Addr:    addr,
			Handler: handler,
		},
		isShuttingDown: false,
	}
}

// TrackStream is called when a user begins a prompt generation request
func (s *GracefulServer) TrackStream() bool {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if s.isShuttingDown {
		// Reject new requests, tell load balancer to route elsewhere
		return false
	}
	s.activeStreams.Add(1)
	return true
}

// ReleaseStream is called when generation is complete
func (s *GracefulServer) ReleaseStream() {
	s.activeStreams.Done()
}

// ListenAndServeWithDrain blocks and runs the server, handling OS interrupts
func (s *GracefulServer) ListenAndServeWithDrain() {
	go func() {
		fmt.Printf("[Server] API Gateway listening on %s\n", s.httpServer.Addr)
		if err := s.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			fmt.Printf("HTTP server error: %v\n", err)
		}
	}()

	// Wait for Kubernetes SIGTERM or Ctrl+C
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	fmt.Println("\n[Server] SIGTERM received. Initiating Graceful Drain...")

	// 1. Mark as shutting down (rejects new connections)
	s.mu.Lock()
	s.isShuttingDown = true
	s.mu.Unlock()

	// 2. Shut down the HTTP listener so K8s stops routing here
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	s.httpServer.Shutdown(ctx)

	// 3. Wait for all active LLM streams to finish
	fmt.Println("[Server] Waiting for active MoE token streams to finish...")

	// Create a channel to wait with a max timeout
	c := make(chan struct{})
	go func() {
		defer close(c)
		s.activeStreams.Wait()
	}()

	select {
	case <-c:
		fmt.Println("[Server] All streams drained successfully. Safe to exit.")
	case <-time.After(30 * time.Second):
		fmt.Println("[Server] Drain timeout (30s) exceeded. Forcing shutdown of remaining streams.")
	}
}

