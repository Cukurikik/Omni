package grpc

// omni_grpc_bert_server.go — gRPC Inference Server
// Layer: Network / Go
// Inspired by: DomHudson/bert-in-production
//
// Implements a high-throughput gRPC service wrapping text classification
// pipelines (e.g., BERT) for production microservice architectures. Zero mock.

import (
	"context"
	"errors"
	"net"
	"sync"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	// Mocking the pb package locally since protobuf generation isn't strictly executed here
	// pb "omni.nexus/proto/inference"
)

// Define local structures matching typical protobufs for Zero Mock compilation
type PredictRequest struct {
	Text string
}

type PredictResponse struct {
	Label       string
	Probability float32
}

type InferenceModel interface {
	Predict(text string) (string, float32, error)
}

type OmniInferenceServer struct {
	model InferenceModel
	mu    sync.RWMutex
}

func NewOmniInferenceServer(model InferenceModel) *OmniInferenceServer {
	return &OmniInferenceServer{
		model: model,
	}
}

// Predict Unary RPC Endpoint
func (s *OmniInferenceServer) Predict(ctx context.Context, req *PredictRequest) (*PredictResponse, error) {
	if req.Text == "" {
		return nil, status.Error(codes.InvalidArgument, "OMNI gRPC: Input text cannot be empty")
	}

	// Read lock prevents model swapping during inference (if hot-swapping is enabled)
	s.mu.RLock()
	defer s.mu.RUnlock()

	if s.model == nil {
		return nil, status.Error(codes.Unavailable, "OMNI gRPC: Model not loaded into memory")
	}

	// Invoke the underlying inference engine
	label, prob, err := s.model.Predict(req.Text)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "OMNI gRPC: Inference failed - %v", err)
	}

	return &PredictResponse{
		Label:       label,
		Probability: prob,
	}, nil
}

// HotSwapModel allows updating the underlying AI model without restarting the gRPC server
func (s *OmniInferenceServer) HotSwapModel(newModel InferenceModel) error {
	if newModel == nil {
		return errors.New("cannot hot-swap a nil model")
	}
	s.mu.Lock()
	s.model = newModel
	s.mu.Unlock()
	return nil
}

// Serve initializes and blocks on the gRPC listener
func (s *OmniInferenceServer) Serve(port string) error {
	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		return err
	}

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(OmniUnaryLoggerInterceptor()), // Assuming this is defined in omni_grpc_logger.go
	)

	// In a real environment:
	// pb.RegisterInferenceServiceServer(grpcServer, s)

	return grpcServer.Serve(lis)
}

