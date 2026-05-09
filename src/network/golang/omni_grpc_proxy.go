package network_golang

import (
	"context"
	"log"
	"net"

	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
)

type OmniProxyServer struct{}

func (s *OmniProxyServer) ProxyInference(ctx context.Context, req interface{}) (interface{}, error) {
	md, ok := metadata.FromIncomingContext(ctx)
	if ok {
		log.Printf("Received proxy request with metadata: %v", md)
	}
	// Route to internal Rust backend
	return map[string]string{"status": "proxied", "node": "rust_core"}, nil
}

func StartProxy(port string) {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	log.Printf("OMNI gRPC Proxy listening on %s", port)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}

