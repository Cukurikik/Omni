package grpc

// omni_grpc_client.go — Production gRPC Client
// Layer: Network / Go
//
// Implements a resilient gRPC client wrapper handling connection pooling,
// exponential backoff retries, and context propagation for OMNI microservices.
// Zero mocks.

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
)

type OmniGrpcClient struct {
	target string
	conn   *grpc.ClientConn
}

// NewOmniGrpcClient creates a new resilient connection to a target service.
func NewOmniGrpcClient(target string) (*OmniGrpcClient, error) {
	opts := []grpc.DialOption{
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithUnaryInterceptor(unaryRetryInterceptor),
	}

	// Dial uses the target URI, which can integrate with Consul/DNS
	conn, err := grpc.Dial(target, opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to dial target %s: %w", target, err)
	}

	return &OmniGrpcClient{
		target: target,
		conn:   conn,
	}, nil
}

// Close gracefully tears down the connection.
func (c *OmniGrpcClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

// GetConn exposes the underlying grpc.ClientConn for generating service stubs.
func (c *OmniGrpcClient) GetConn() *grpc.ClientConn {
	return c.conn
}

// unaryRetryInterceptor implements exponential backoff for transient gRPC errors.
func unaryRetryInterceptor(
	ctx context.Context,
	method string,
	req, reply interface{},
	cc *grpc.ClientConn,
	invoker grpc.UnaryInvoker,
	opts ...grpc.CallOption,
) error {
	maxRetries := 3
	baseDelay := 100 * time.Millisecond

	var err error
	for attempt := 0; attempt <= maxRetries; attempt++ {
		err = invoker(ctx, method, req, reply, cc, opts...)
		if err == nil {
			return nil
		}

		st, _ := status.FromError(err)

		// Only retry on transient codes
		switch st.Code() {
		case codes.Unavailable, codes.DeadlineExceeded, codes.ResourceExhausted:
			if attempt == maxRetries {
				return err
			}

			// Exponential backoff
			delay := baseDelay * (1 << attempt)

			select {
			case <-time.After(delay):
				// wait completed
			case <-ctx.Done():
				return ctx.Err() // Context cancelled by user/timeout
			}
		default:
			// Non-retriable error
			return err
		}
	}
	return err
}

