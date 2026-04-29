package bentoml

import (
	"errors"
	"context"
	"sync"
)

type ModelRequest struct {
	Features []float32
}

type ModelResponse struct {
	Prediction float32
}

type BentoServer struct {
	mu sync.RWMutex
	isActive bool
}

func NewBentoServer() *BentoServer {
	return &BentoServer{isActive: true}
}

func (s *BentoServer) Predict(ctx context.Context, req *ModelRequest) (*ModelResponse, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if !s.isActive {
		return nil, errors.New("server is shutting down")
	}

	// Simulated mathematical prediction
	var sum float32 = 0
	for _, f := range req.Features {
		sum += f * 0.5
	}

	return &ModelResponse{Prediction: sum}, nil
}
