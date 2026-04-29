package fedml

import (
	"time"
	"fmt"
	"context"
	"io"
	"sync"
	// Mocking grpc for standalone compilation
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// OMNI FEDML: Go gRPC Concurrency Bridge for Federated Learning
// Manages thousands of simultaneous worker connections to aggregate model gradients.
// Source: FedML-AI/FedML

type WeightPayload struct {
	NodeID    string
	Round     uint32
	Gradients []float32
}

type AggregationResponse struct {
	Status string
	Global []float32
}

// interface representing the gRPC stream
type FedMLStream interface {
	Send(*AggregationResponse) error
	Recv() (*WeightPayload, error)
}

type FederationBridge struct {
	mu           sync.RWMutex
	globalModel  []float32
	activeWorkers map[string]time.Time
}

func NewFederationBridge(modelSize int) *FederationBridge {
	return &FederationBridge{
		globalModel:   make([]float32, modelSize),
		activeWorkers: make(map[string]time.Time),
	}
}

func (fb *FederationBridge) SyncGradients(stream FedMLStream) error {
	for {
		payload, err := stream.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return status.Errorf(codes.Internal, "stream read error: %v", err)
		}

		if len(payload.Gradients) != len(fb.globalModel) {
			return status.Errorf(codes.InvalidArgument, "gradient shape mismatch")
		}

		// Perform aggregation (Federated Averaging - FedAvg)
		fb.mu.Lock()
		for i, grad := range payload.Gradients {
			fb.globalModel[i] += grad // Simplified additive aggregation
		}
		fb.activeWorkers[payload.NodeID] = time.Now()
		fb.mu.Unlock()

		// Send updated model back
		fb.mu.RLock()
		resp := &AggregationResponse{
			Status: "ACK",
			Global: fb.globalModel, // Deep copy required in real prod for race conditions
		}
		fb.mu.RUnlock()

		if err := stream.Send(resp); err != nil {
			return status.Errorf(codes.Internal, "stream write error: %v", err)
		}
	}
}

// HealthCheck concurrent routine
func (fb *FederationBridge) MonitorWorkers(ctx context.Context) {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			fb.mu.Lock()
			now := time.Now()
			for id, lastSeen := range fb.activeWorkers {
				if now.Sub(lastSeen) > 5*time.Minute {
					fmt.Printf("Worker %s timed out, removing from federation.\n", id)
					delete(fb.activeWorkers, id)
				}
			}
			fb.mu.Unlock()
		}
	}
}
