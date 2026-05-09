// OMNI Network Layer — Go gRPC Inference Service
// Production model serving gateway with health checks, metrics, streaming.
// Learned from: vLLM serving patterns, Triton Inference Server

package serving

import (
	"context"
	"fmt"
	"log"
	"net"
	"sync"
	"sync/atomic"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

// InferenceRequest represents a model inference request
type InferenceRequest struct {
	RequestID   string
	InputText   string
	MaxTokens   int
	Temperature float64
	TopK        int
	TopP        float64
	Stream      bool
	CreatedAt   time.Time
}

// InferenceResponse represents a model inference response
type InferenceResponse struct {
	RequestID       string
	GeneratedText   string
	TokensGenerated int
	LatencyMs       float64
	FinishReason    string
}

// ServerMetrics tracks inference server performance
type ServerMetrics struct {
	TotalRequests  atomic.Int64
	ActiveRequests atomic.Int64
	TotalTokens    atomic.Int64
	TotalLatencyMs atomic.Int64
	ErrorCount     atomic.Int64
}

func (m *ServerMetrics) RecordRequest(latencyMs float64, tokens int) {
	m.TotalRequests.Add(1)
	m.TotalTokens.Add(int64(tokens))
	m.TotalLatencyMs.Add(int64(latencyMs))
}

func (m *ServerMetrics) AvgLatencyMs() float64 {
	total := m.TotalRequests.Load()
	if total == 0 {
		return 0
	}
	return float64(m.TotalLatencyMs.Load()) / float64(total)
}

// RequestQueue implements continuous batching for inference
type RequestQueue struct {
	mu         sync.Mutex
	queue      []*pendingRequest
	maxBatch   int
	maxWait    time.Duration
	notifyChan chan struct{}
}

type pendingRequest struct {
	req    *InferenceRequest
	result chan *InferenceResponse
}

func NewRequestQueue(maxBatch int, maxWait time.Duration) *RequestQueue {
	return &RequestQueue{
		queue:      make([]*pendingRequest, 0, maxBatch),
		maxBatch:   maxBatch,
		maxWait:    maxWait,
		notifyChan: make(chan struct{}, 1),
	}
}

func (q *RequestQueue) Enqueue(req *InferenceRequest) <-chan *InferenceResponse {
	q.mu.Lock()
	defer q.mu.Unlock()

	ch := make(chan *InferenceResponse, 1)
	q.queue = append(q.queue, &pendingRequest{req: req, result: ch})

	select {
	case q.notifyChan <- struct{}{}:
	default:
	}

	return ch
}

func (q *RequestQueue) DequeueeBatch() []*pendingRequest {
	q.mu.Lock()
	defer q.mu.Unlock()

	n := len(q.queue)
	if n > q.maxBatch {
		n = q.maxBatch
	}
	if n == 0 {
		return nil
	}

	batch := make([]*pendingRequest, n)
	copy(batch, q.queue[:n])
	q.queue = q.queue[n:]
	return batch
}

// InferenceServer is the main gRPC serving infrastructure
type InferenceServer struct {
	metrics   *ServerMetrics
	queue     *RequestQueue
	grpcSrv   *grpc.Server
	healthSrv *health.Server
	addr      string
	handler   InferenceHandler
	stopChan  chan struct{}
}

// InferenceHandler processes batched inference requests
type InferenceHandler interface {
	ProcessBatch(ctx context.Context, requests []*InferenceRequest) ([]*InferenceResponse, error)
	HealthCheck() error
}

func NewInferenceServer(addr string, handler InferenceHandler, maxBatch int) *InferenceServer {
	return &InferenceServer{
		metrics:  &ServerMetrics{},
		queue:    NewRequestQueue(maxBatch, 50*time.Millisecond),
		addr:     addr,
		handler:  handler,
		stopChan: make(chan struct{}),
	}
}

func (s *InferenceServer) Start() error {
	lis, err := net.Listen("tcp", s.addr)
	if err != nil {
		return fmt.Errorf("failed to listen on %s: %w", s.addr, err)
	}

	s.grpcSrv = grpc.NewServer(
		grpc.MaxRecvMsgSize(64*1024*1024),
		grpc.MaxSendMsgSize(64*1024*1024),
	)

	s.healthSrv = health.NewServer()
	healthpb.RegisterHealthServer(s.grpcSrv, s.healthSrv)
	s.healthSrv.SetServingStatus("inference", healthpb.HealthCheckResponse_SERVING)

	// Start batch processing loop
	go s.batchLoop()

	log.Printf("OMNI Inference Server listening on %s", s.addr)
	return s.grpcSrv.Serve(lis)
}

func (s *InferenceServer) batchLoop() {
	for {
		select {
		case <-s.stopChan:
			return
		case <-s.queue.notifyChan:
			batch := s.queue.DequeueeBatch()
			if len(batch) == 0 {
				continue
			}

			s.metrics.ActiveRequests.Add(int64(len(batch)))
			start := time.Now()

			requests := make([]*InferenceRequest, len(batch))
			for i, p := range batch {
				requests[i] = p.req
			}

			ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
			responses, err := s.handler.ProcessBatch(ctx, requests)
			cancel()

			latency := float64(time.Since(start).Milliseconds())

			for i, p := range batch {
				if err != nil {
					p.result <- &InferenceResponse{
						RequestID:    p.req.RequestID,
						FinishReason: fmt.Sprintf("error: %v", err),
					}
					s.metrics.ErrorCount.Add(1)
				} else if i < len(responses) {
					responses[i].LatencyMs = latency
					p.result <- responses[i]
					s.metrics.RecordRequest(latency, responses[i].TokensGenerated)
				}
				close(p.result)
			}
			s.metrics.ActiveRequests.Add(-int64(len(batch)))
		}
	}
}

func (s *InferenceServer) Stop() {
	close(s.stopChan)
	s.healthSrv.SetServingStatus("inference", healthpb.HealthCheckResponse_NOT_SERVING)
	s.grpcSrv.GracefulStop()
	log.Printf("Server stopped. Total requests: %d, Avg latency: %.1fms",
		s.metrics.TotalRequests.Load(), s.metrics.AvgLatencyMs())
}
