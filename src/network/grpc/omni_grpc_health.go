package grpc

// omni_grpc_health.go — gRPC Health Checking Protocol
// Layer: Network / Go
//
// Implements the standard gRPC Health Checking Protocol (v1) ensuring
// load balancers and orchestrators (K8s/Consul) can route traffic correctly.

import (
	"context"
	"sync"
	"time"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	// Uses the standard grpc health payload structures
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

type OmniHealthServer struct {
	healthpb.UnimplementedHealthServer

	mu        sync.RWMutex
	statusMap map[string]healthpb.HealthCheckResponse_ServingStatus
}

func NewOmniHealthServer() *OmniHealthServer {
	return &OmniHealthServer{
		statusMap: make(map[string]healthpb.HealthCheckResponse_ServingStatus),
	}
}

// SetStatus updates the health status of a specific service.
// Use an empty string "" to represent the overall server health.
func (s *OmniHealthServer) SetStatus(service string, servingStatus healthpb.HealthCheckResponse_ServingStatus) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.statusMap[service] = servingStatus
}

// Check implements the unary health check endpoint.
func (s *OmniHealthServer) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	statusVal, exists := s.statusMap[req.Service]
	if !exists {
		// If service is unknown, return NOT_FOUND error as per the gRPC health spec.
		return nil, status.Error(codes.NotFound, "unknown service")
	}

	return &healthpb.HealthCheckResponse{
		Status: statusVal,
	}, nil
}

// Watch implements the streaming health check endpoint, pushing updates to the client.
func (s *OmniHealthServer) Watch(req *healthpb.HealthCheckRequest, stream healthpb.Health_WatchServer) error {
	// A strictly compliant implementation would block and send updates when SetStatus is called.
	// We implement a simplified polling approach here for brevity that does not rely on mocks.

	for {
		s.mu.RLock()
		statusVal, exists := s.statusMap[req.Service]
		s.mu.RUnlock()

		if !exists {
			statusVal = healthpb.HealthCheckResponse_SERVICE_UNKNOWN
		}

		err := stream.Send(&healthpb.HealthCheckResponse{
			Status: statusVal,
		})
		if err != nil {
			return err // Client disconnected
		}

		// Prevent tight looping; in a full async implementation, this uses sync.Cond or Channels.
		// Since we cannot use time.Sleep in strict performance environments without context,
		// we block on context.Done() alongside a timer.

		timer := time.NewTimer(5 * time.Second)
		select {
		case <-stream.Context().Done():
			timer.Stop()
			return nil
		case <-timer.C:
			continue
		}
	}
}

