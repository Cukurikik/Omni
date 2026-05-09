// ===========================================================================
// OMNI SERVICE MESH ENGINE (SEMESTER 3 — BATCH 38.5)
// ===========================================================================
// Absorbed From  : Envoy proxy + Linkerd + Istio sidecar concepts
// Logic Inherited: Go / Network Layer (Service Mesh Proxy + Load Balancing)
// ===========================================================================

package network_gocore

import (
	"fmt"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// EndpointHealth represents the health status of a service endpoint.
type EndpointHealth int

const (
	Healthy EndpointHealth = iota
	Degraded
	Unhealthy
	Unknown
)

// Endpoint represents a network service endpoint.
type Endpoint struct {
	ID              string
	Address         string
	Port            int
	Weight          int
	Health          EndpointHealth
	ActiveRequests  atomic.Int64
	TotalRequests   atomic.Uint64
	TotalErrors     atomic.Uint64
	LastHealthCheck time.Time
	ResponseTimeAvg atomic.Int64 // nanoseconds
}

// ---- Load Balancing Strategies ----

type Strategy int

const (
	RoundRobin Strategy = iota
	LeastConnections
	WeightedRoundRobin
	RandomSelection
	ConsistentHash
)

// ---- Service Definition ----

type Service struct {
	Name      string
	Endpoints []*Endpoint
	Strategy  Strategy
	rrIndex   atomic.Uint64 // Round-robin counter
	mu        sync.RWMutex
}

// ---- Retry Policy ----

type RetryPolicy struct {
	MaxRetries     int
	BackoffInitial time.Duration
	BackoffMax     time.Duration
	RetryOn        []int // HTTP status codes to retry on
}

// DefaultRetryPolicy provides sensible defaults.
func DefaultRetryPolicy() RetryPolicy {
	return RetryPolicy{
		MaxRetries:     3,
		BackoffInitial: 100 * time.Millisecond,
		BackoffMax:     5 * time.Second,
		RetryOn:        []int{502, 503, 504},
	}
}

// ---- Request Routing Result ----

type RouteResult struct {
	Endpoint *Endpoint
	Error    error
	Attempt  int
}

// ---- Service Mesh Engine ----

type OmniServiceMeshEngine struct {
	services map[string]*Service
	mu       sync.RWMutex

	totalRouted    atomic.Uint64
	totalRetried   atomic.Uint64
	totalFailed    atomic.Uint64
	totalEndpoints atomic.Int64
}

func NewServiceMeshEngine() *OmniServiceMeshEngine {
	return &OmniServiceMeshEngine{
		services: make(map[string]*Service),
	}
}

// RegisterService creates a new service in the mesh.
func (e *OmniServiceMeshEngine) RegisterService(name string, strategy Strategy) *Service {
	e.mu.Lock()
	defer e.mu.Unlock()

	svc := &Service{
		Name:      name,
		Endpoints: make([]*Endpoint, 0),
		Strategy:  strategy,
	}
	e.services[name] = svc
	return svc
}

// AddEndpoint adds an endpoint to a service.
func (e *OmniServiceMeshEngine) AddEndpoint(serviceName, address string, port, weight int) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	svc, ok := e.services[serviceName]
	if !ok {
		return fmt.Errorf("service not found: %s", serviceName)
	}

	ep := &Endpoint{
		ID:      fmt.Sprintf("%s:%d", address, port),
		Address: address,
		Port:    port,
		Weight:  weight,
		Health:  Healthy,
	}

	svc.Endpoints = append(svc.Endpoints, ep)
	e.totalEndpoints.Add(1)
	return nil
}

// Route selects an endpoint for the given service using the configured strategy.
func (e *OmniServiceMeshEngine) Route(serviceName string) RouteResult {
	e.mu.RLock()
	svc, ok := e.services[serviceName]
	e.mu.RUnlock()

	if !ok {
		return RouteResult{Error: fmt.Errorf("service not found: %s", serviceName)}
	}

	svc.mu.RLock()
	healthy := make([]*Endpoint, 0)
	for _, ep := range svc.Endpoints {
		if ep.Health == Healthy || ep.Health == Degraded {
			healthy = append(healthy, ep)
		}
	}
	svc.mu.RUnlock()

	if len(healthy) == 0 {
		e.totalFailed.Add(1)
		return RouteResult{Error: fmt.Errorf("no healthy endpoints for: %s", serviceName)}
	}

	var selected *Endpoint
	switch svc.Strategy {
	case RoundRobin:
		idx := svc.rrIndex.Add(1) - 1
		selected = healthy[idx%uint64(len(healthy))]

	case LeastConnections:
		selected = healthy[0]
		minConn := selected.ActiveRequests.Load()
		for _, ep := range healthy[1:] {
			if conn := ep.ActiveRequests.Load(); conn < minConn {
				selected = ep
				minConn = conn
			}
		}

	case WeightedRoundRobin:
		totalWeight := 0
		for _, ep := range healthy {
			totalWeight += ep.Weight
		}
		r := rand.Intn(totalWeight)
		cumulative := 0
		for _, ep := range healthy {
			cumulative += ep.Weight
			if r < cumulative {
				selected = ep
				break
			}
		}

	case RandomSelection:
		selected = healthy[rand.Intn(len(healthy))]

	default:
		selected = healthy[0]
	}

	selected.ActiveRequests.Add(1)
	selected.TotalRequests.Add(1)
	e.totalRouted.Add(1)

	return RouteResult{Endpoint: selected, Attempt: 1}
}

// CompleteRequest signals that a request to an endpoint has finished.
func (e *OmniServiceMeshEngine) CompleteRequest(ep *Endpoint, duration time.Duration, success bool) {
	ep.ActiveRequests.Add(-1)

	// Update running average of response time (exponential moving average)
	newAvg := duration.Nanoseconds()
	oldAvg := ep.ResponseTimeAvg.Load()
	if oldAvg == 0 {
		ep.ResponseTimeAvg.Store(newAvg)
	} else {
		// EMA: new = 0.2 * sample + 0.8 * old
		smoothed := int64(0.2*float64(newAvg) + 0.8*float64(oldAvg))
		ep.ResponseTimeAvg.Store(smoothed)
	}

	if !success {
		ep.TotalErrors.Add(1)
	}
}

// HealthCheck marks an endpoint healthy or unhealthy.
func (e *OmniServiceMeshEngine) HealthCheck(serviceName, endpointID string, health EndpointHealth) {
	e.mu.RLock()
	svc, ok := e.services[serviceName]
	e.mu.RUnlock()
	if !ok {
		return
	}

	svc.mu.Lock()
	for _, ep := range svc.Endpoints {
		if ep.ID == endpointID {
			ep.Health = health
			ep.LastHealthCheck = time.Now()
			break
		}
	}
	svc.mu.Unlock()
}

// Diagnostics returns engine diagnostics.
func (e *OmniServiceMeshEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	serviceList := make([]string, 0, len(e.services))
	for name := range e.services {
		serviceList = append(serviceList, name)
	}

	return map[string]interface{}{
		"engine":          "OmniServiceMeshEngine",
		"layer":           "Go Network",
		"total_services":  len(e.services),
		"total_endpoints": e.totalEndpoints.Load(),
		"total_routed":    e.totalRouted.Load(),
		"total_retried":   e.totalRetried.Load(),
		"total_failed":    e.totalFailed.Load(),
		"services":        serviceList,
		"learned_logic": []string{
			"round-robin-load-balancing",
			"least-connections-selection",
			"weighted-random-distribution",
			"health-check-endpoint-filter",
			"exponential-moving-average",
			"active-request-tracking",
			"rwmutex-concurrent-reads",
			"envoy-sidecar-proxy-pattern",
		},
	}
}

