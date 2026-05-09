package gpt4all

import (
	"context"
	"fmt"
	"time"
)

// OMNI GPT4ALL: Edge Telemetry Client (Go)
// gRPC-like event emitter that sends hardware metrics from edge devices back to the central cloud.
// Source: nomic-ai/gpt4all

type EdgeMetrics struct {
	DeviceID     string
	ModelName    string
	CPUUsagePct  float64
	RAMUsageMB   int
	TokensPerSec float64
	Timestamp    int64
}

type EdgeTelemetryClient struct {
	telemetryChan chan EdgeMetrics
	serverURL     string
}

func NewEdgeTelemetryClient(serverURL string, bufferSize int) *EdgeTelemetryClient {
	return &EdgeTelemetryClient{
		telemetryChan: make(chan EdgeMetrics, bufferSize),
		serverURL:     serverURL,
	}
}

// Emits metrics locally to the buffer
func (c *EdgeTelemetryClient) Emit(deviceID, model string, cpu float64, ram int, tps float64) {
	metrics := EdgeMetrics{
		DeviceID:     deviceID,
		ModelName:    model,
		CPUUsagePct:  cpu,
		RAMUsageMB:   ram,
		TokensPerSec: tps,
		Timestamp:    time.Now().Unix(),
	}

	select {
	case c.telemetryChan <- metrics:
	default:
		// Edge devices should drop telemetry rather than block inference
		fmt.Println("[Warning] Edge Telemetry buffer full, dropping payload.")
	}
}

// Background loop simulating gRPC push to cloud
func (c *EdgeTelemetryClient) StartCloudSync(ctx context.Context) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("Shutting down Edge Telemetry sync.")
				return
			case m := <-c.telemetryChan:
				// Simulated network push
				fmt.Printf("[Syncing to %s] Device: %s | Model: %s | TPS: %.1f\n",
					c.serverURL, m.DeviceID, m.ModelName, m.TokensPerSec)
			}
		}
	}()
}
