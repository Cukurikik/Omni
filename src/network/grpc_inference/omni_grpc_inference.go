// omni_grpc_inference.go — gRPC Inference Service
// Inspired by: TensorRT Inference Server + OMNI serving
// Layer: Network / Go
//
// High-performance gRPC server for model inference with
// streaming, health probes, and Prometheus metrics.

package grpc_inference

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"sync/atomic"
	"time"
)

type InferRequest struct {
	ModelName    string               `json:"model_name"`
	ModelVersion string               `json:"model_version,omitempty"`
	Inputs       map[string][]float32 `json:"inputs"`
	Parameters   map[string]string    `json:"parameters,omitempty"`
	RequestID    string               `json:"request_id"`
}

type InferResponse struct {
	ModelName    string               `json:"model_name"`
	ModelVersion string               `json:"model_version"`
	Outputs      map[string][]float32 `json:"outputs"`
	RequestID    string               `json:"request_id"`
	LatencyMs    float64              `json:"latency_ms"`
}

type ModelInfo struct {
	Name     string   `json:"name"`
	Version  string   `json:"version"`
	Platform string   `json:"platform"`
	Inputs   []IOSpec `json:"inputs"`
	Outputs  []IOSpec `json:"outputs"`
	Status   string   `json:"status"`
}

type IOSpec struct {
	Name     string  `json:"name"`
	DataType string  `json:"data_type"`
	Shape    []int64 `json:"shape"`
}

type InferenceBackend interface {
	Predict(ctx context.Context, req *InferRequest) (*InferResponse, error)
	GetModelInfo(modelName string) (*ModelInfo, error)
	IsReady(modelName string) bool
}

type ServerMetrics struct {
	TotalRequests   atomic.Int64
	SuccessRequests atomic.Int64
	FailedRequests  atomic.Int64
	TotalLatencyUs  atomic.Int64
	ActiveRequests  atomic.Int64
}

func (m *ServerMetrics) RecordRequest(latencyUs int64, success bool) {
	m.TotalRequests.Add(1)
	m.TotalLatencyUs.Add(latencyUs)
	if success {
		m.SuccessRequests.Add(1)
	} else {
		m.FailedRequests.Add(1)
	}
}

func (m *ServerMetrics) AvgLatencyMs() float64 {
	total := m.TotalRequests.Load()
	if total == 0 {
		return 0
	}
	return float64(m.TotalLatencyUs.Load()) / float64(total) / 1000.0
}

func (m *ServerMetrics) ErrorRate() float64 {
	total := m.TotalRequests.Load()
	if total == 0 {
		return 0
	}
	return float64(m.FailedRequests.Load()) / float64(total)
}

type RequestInterceptor func(req *InferRequest) error

type OmniGRPCInferenceServer struct {
	backend       InferenceBackend
	metrics       *ServerMetrics
	interceptors  []RequestInterceptor
	mu            sync.RWMutex
	maxConcurrent int
	semaphore     chan struct{}
}

func NewOmniGRPCServer(backend InferenceBackend, maxConcurrent int) *OmniGRPCInferenceServer {
	return &OmniGRPCInferenceServer{
		backend:       backend,
		metrics:       &ServerMetrics{},
		interceptors:  make([]RequestInterceptor, 0),
		maxConcurrent: maxConcurrent,
		semaphore:     make(chan struct{}, maxConcurrent),
	}
}

func (s *OmniGRPCInferenceServer) AddInterceptor(interceptor RequestInterceptor) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.interceptors = append(s.interceptors, interceptor)
}

func (s *OmniGRPCInferenceServer) Infer(ctx context.Context, req *InferRequest) (*InferResponse, error) {
	// Acquire semaphore for concurrency control
	select {
	case s.semaphore <- struct{}{}:
		defer func() { <-s.semaphore }()
	case <-ctx.Done():
		return nil, ctx.Err()
	}

	s.metrics.ActiveRequests.Add(1)
	defer s.metrics.ActiveRequests.Add(-1)

	start := time.Now()

	// Run interceptors
	s.mu.RLock()
	interceptors := s.interceptors
	s.mu.RUnlock()

	for _, interceptor := range interceptors {
		if err := interceptor(req); err != nil {
			latencyUs := time.Since(start).Microseconds()
			s.metrics.RecordRequest(latencyUs, false)
			return nil, fmt.Errorf("interceptor failed: %w", err)
		}
	}

	// Validate request
	if err := s.validateRequest(req); err != nil {
		latencyUs := time.Since(start).Microseconds()
		s.metrics.RecordRequest(latencyUs, false)
		return nil, err
	}

	// Execute inference
	resp, err := s.backend.Predict(ctx, req)
	latencyUs := time.Since(start).Microseconds()

	if err != nil {
		s.metrics.RecordRequest(latencyUs, false)
		return nil, fmt.Errorf("inference failed: %w", err)
	}

	resp.LatencyMs = float64(latencyUs) / 1000.0
	s.metrics.RecordRequest(latencyUs, true)

	return resp, nil
}

func (s *OmniGRPCInferenceServer) InferStream(ctx context.Context, req *InferRequest, resultCh chan<- *InferResponse) error {
	defer close(resultCh)

	s.metrics.ActiveRequests.Add(1)
	defer s.metrics.ActiveRequests.Add(-1)

	// For streaming: we chunk the output
	fullResp, err := s.backend.Predict(ctx, req)
	if err != nil {
		return err
	}

	// Send in chunks
	chunkSize := 64
	for name, data := range fullResp.Outputs {
		for i := 0; i < len(data); i += chunkSize {
			end := i + chunkSize
			if end > len(data) {
				end = len(data)
			}

			chunk := &InferResponse{
				ModelName:    fullResp.ModelName,
				ModelVersion: fullResp.ModelVersion,
				Outputs:      map[string][]float32{name: data[i:end]},
				RequestID:    fullResp.RequestID,
			}

			select {
			case resultCh <- chunk:
			case <-ctx.Done():
				return ctx.Err()
			}
		}
	}

	return nil
}

func (s *OmniGRPCInferenceServer) GetModelMetadata(modelName string) (*ModelInfo, error) {
	return s.backend.GetModelInfo(modelName)
}

func (s *OmniGRPCInferenceServer) HealthCheck() map[string]interface{} {
	return map[string]interface{}{
		"status":           "serving",
		"total_requests":   s.metrics.TotalRequests.Load(),
		"success_requests": s.metrics.SuccessRequests.Load(),
		"failed_requests":  s.metrics.FailedRequests.Load(),
		"active_requests":  s.metrics.ActiveRequests.Load(),
		"avg_latency_ms":   s.metrics.AvgLatencyMs(),
		"error_rate":       s.metrics.ErrorRate(),
	}
}

func (s *OmniGRPCInferenceServer) validateRequest(req *InferRequest) error {
	if req.ModelName == "" {
		return fmt.Errorf("model_name is required")
	}
	if len(req.Inputs) == 0 {
		return fmt.Errorf("at least one input tensor is required")
	}
	if !s.backend.IsReady(req.ModelName) {
		return fmt.Errorf("model %s is not ready", req.ModelName)
	}
	return nil
}

func (s *OmniGRPCInferenceServer) MetricsJSON() ([]byte, error) {
	return json.Marshal(s.HealthCheck())
}

// Logging interceptor
func LoggingInterceptor() RequestInterceptor {
	return func(req *InferRequest) error {
		log.Printf("[INFER] model=%s version=%s request_id=%s inputs=%d",
			req.ModelName, req.ModelVersion, req.RequestID, len(req.Inputs))
		return nil
	}
}

// Validation interceptor
func InputValidationInterceptor(maxInputSize int) RequestInterceptor {
	return func(req *InferRequest) error {
		for name, data := range req.Inputs {
			if len(data) > maxInputSize {
				return fmt.Errorf("input %s exceeds max size: %d > %d",
					name, len(data), maxInputSize)
			}
		}
		return nil
	}
}
