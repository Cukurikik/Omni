package network_go

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/health/grpc_health_v1"
)

// OMNI MOTHER: Expert Health Checker
// Actively pings expert nodes via gRPC Health Checking Protocol

type HealthChecker struct {
	interval time.Duration
	timeout  time.Duration
}

func NewHealthChecker(interval, timeout time.Duration) *HealthChecker {
	return &HealthChecker{
		interval: interval,
		timeout:  timeout,
	}
}

func (hc *HealthChecker) Monitor(address string, statusChan chan<- bool) {
	ticker := time.NewTicker(hc.interval)
	for range ticker.C {
		status := hc.check(address)
		statusChan <- status
	}
}

func (hc *HealthChecker) check(address string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), hc.timeout)
	defer cancel()

	conn, err := grpc.DialContext(ctx, address, grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithBlock())
	if err != nil {
		log.Printf("OMNI WARN: Health check failed to connect to %s: %v", address, err)
		return false
	}
	defer conn.Close()

	client := grpc_health_v1.NewHealthClient(conn)
	resp, err := client.Check(ctx, &grpc_health_v1.HealthCheckRequest{Service: "ExpertService"})
	if err != nil {
		log.Printf("OMNI WARN: Health check RPC failed for %s: %v", address, err)
		return false
	}

	return resp.Status == grpc_health_v1.HealthCheckResponse_SERVING
}

