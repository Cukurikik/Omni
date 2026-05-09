// omni_grpc_interceptor.go — gRPC Interceptor
// Layer: Network / Go
//
// Unary and Stream gRPC interceptors to provide centralized logging,
// telemetry, and authentication checks before requests hit the handlers.

package grpc

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

// OmniUnaryInterceptor is a gRPC interceptor for logging and auth on unary calls.
func OmniUnaryInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {

	start := time.Now()

	// 1. Extract Metadata (Headers)
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return nil, status.Error(codes.Unauthenticated, "Missing metadata")
	}

	// 2. Simple Mock Authentication
	authHeaders := md["authorization"]
	if len(authHeaders) == 0 {
		return nil, status.Error(codes.Unauthenticated, "Authorization token required")
	}

	// Mock: Reject if not "Bearer valid-omni-token"
	if authHeaders[0] != "Bearer valid-omni-token" {
		return nil, status.Error(codes.PermissionDenied, "Invalid authentication token")
	}

	// 3. Handle the request
	resp, err := handler(ctx, req)

	// 4. Telemetry and Logging
	duration := time.Since(start)
	if err != nil {
		log.Printf("[gRPC] %s FAILED in %v. Error: %v", info.FullMethod, duration, err)
	} else {
		log.Printf("[gRPC] %s OK in %v", info.FullMethod, duration)
	}

	return resp, err
}

// OmniStreamInterceptor handles streams, wrapping the ServerStream to intercept recv/send.
func OmniStreamInterceptor(
	srv interface{},
	ss grpc.ServerStream,
	info *grpc.StreamServerInfo,
	handler grpc.StreamHandler,
) error {
	log.Printf("[gRPC Stream] Started: %s", info.FullMethod)

	err := handler(srv, ss)

	if err != nil {
		log.Printf("[gRPC Stream] Finished %s with ERROR: %v", info.FullMethod, err)
	} else {
		log.Printf("[gRPC Stream] Finished %s OK", info.FullMethod)
	}

	return err
}

