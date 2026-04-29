package higgsfield

import (
	"time"
	"fmt"
	"context"
	"net/http"
)

// OMNI Higgsfield - Fault Tolerance Monitor
// Go routines for highly concurrent health checking of distributed training nodes

type NodeStatus string

const (
	StatusHealthy  NodeStatus = "HEALTHY"
	StatusDegraded NodeStatus = "DEGRADED"
	StatusDead     NodeStatus = "DEAD"
)

type NodeHealth struct {
	NodeID string
	Status NodeStatus
	Error  error
}

type HealthMonitor struct {
	Endpoints []string
	Timeout   time.Duration
	Interval  time.Duration
}

func NewHealthMonitor(endpoints []string, timeout, interval time.Duration) *HealthMonitor {
	return &HealthMonitor{
		Endpoints: endpoints,
		Timeout:   timeout,
		Interval:  interval,
	}
}

// CheckNode executes a strict timeout-bound HTTP check
func (hm *HealthMonitor) CheckNode(ctx context.Context, endpoint string) NodeHealth {
	reqCtx, cancel := context.WithTimeout(ctx, hm.Timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(reqCtx, "GET", fmt.Sprintf("http://%s/health", endpoint), nil)
	if err != nil {
		return NodeHealth{NodeID: endpoint, Status: StatusDead, Error: err}
	}

	client := &http.Client{}
	resp, err := client.Do(req)

	if err != nil {
		return NodeHealth{NodeID: endpoint, Status: StatusDead, Error: err}
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		return NodeHealth{NodeID: endpoint, Status: StatusHealthy, Error: nil}
	}

	return NodeHealth{NodeID: endpoint, Status: StatusDegraded, Error: fmt.Errorf("unexpected status code: %d", resp.StatusCode)}
}

// Start polling all nodes concurrently
func (hm *HealthMonitor) Start(ctx context.Context, results chan<- NodeHealth) {
	ticker := time.NewTicker(hm.Interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			for _, endpoint := range hm.Endpoints {
				go func(ep string) {
					health := hm.CheckNode(ctx, ep)
					results <- health
				}(endpoint)
			}
		}
	}
}
