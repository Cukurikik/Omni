package grpc

// omni_grpc_logger.go — gRPC Interceptor Logging
// Layer: Network / Go
//
// Implements strict gRPC Unary and Stream interceptors to log all requests,
// latencies, and status codes cleanly to standard output/logs. Zero mock.

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/peer"
	"google.golang.org/grpc/status"
)

// OmniUnaryLoggerInterceptor logs unary gRPC calls.
func OmniUnaryLoggerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		start := time.Now()

		// Extract caller IP
		var clientIP string
		if p, ok := peer.FromContext(ctx); ok {
			clientIP = p.Addr.String()
		} else {
			clientIP = "unknown"
		}

		resp, err := handler(ctx, req)
		duration := time.Since(start)

		st, _ := status.FromError(err)

		log.Printf("[OMNI gRPC] | %s | %s | %v | %s",
			clientIP,
			info.FullMethod,
			duration,
			st.Code().String(),
		)

		return resp, err
	}
}

// OmniStreamLoggerInterceptor logs streaming gRPC calls.
func OmniStreamLoggerInterceptor() grpc.StreamServerInterceptor {
	return func(
		srv interface{},
		ss grpc.ServerStream,
		info *grpc.StreamServerInfo,
		handler grpc.StreamHandler,
	) error {
		start := time.Now()

		var clientIP string
		if p, ok := peer.FromContext(ss.Context()); ok {
			clientIP = p.Addr.String()
		} else {
			clientIP = "unknown"
		}

		err := handler(srv, ss)
		duration := time.Since(start)

		st, _ := status.FromError(err)

		log.Printf("[OMNI gRPC Stream] | %s | %s | %v | %s",
			clientIP,
			info.FullMethod,
			duration,
			st.Code().String(),
		)

		return err
	}
}

