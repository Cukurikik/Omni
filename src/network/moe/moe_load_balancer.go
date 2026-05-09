// moe_load_balancer.go — Expert-Aware Load Balancer
// Layer: Network / Concurrency — MoE Request Distribution
//
// Distributes inference requests across MoE expert shards using
// expert-aware weighted routing. Considers expert utilization,
// shard health, and pending queue depth for optimal distribution.

package network_moe

import (
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"
)

// BackendState represents a shard backend's runtime state.
type BackendState struct {
	ShardID        int
	Host           string
	Port           int
	IsAlive        bool
	PendingCount   atomic.Int64
	CompletedCount atomic.Int64
	ErrorCount     atomic.Int64
	AvgLatencyUs   atomic.Int64
	ExpertRange    [2]int
	LastHealthy    time.Time
	Weight         float64
	mu             sync.Mutex
}

func (b *BackendState) RecordStart() {
	b.PendingCount.Add(1)
}

func (b *BackendState) RecordComplete(latencyUs int64) {
	b.PendingCount.Add(-1)
	b.CompletedCount.Add(1)
	// Exponential moving average of latency
	old := b.AvgLatencyUs.Load()
	alpha := int64(20) // 5% smoothing
	newAvg := (old*(100-alpha) + latencyUs*alpha) / 100
	b.AvgLatencyUs.Store(newAvg)
}

func (b *BackendState) RecordError() {
	b.PendingCount.Add(-1)
	b.ErrorCount.Add(1)
}

func (b *BackendState) Score() float64 {
	if !b.IsAlive {
		return math.Inf(1) // infinite = never select
	}
	pending := float64(b.PendingCount.Load())
	latency := float64(b.AvgLatencyUs.Load()) / 1000.0 // ms
	errors := float64(b.ErrorCount.Load())
	// Lower is better: pending * 10 + latency + errors * 100
	return pending*10.0 + latency + errors*100.0
}

// LoadBalanceStrategy defines the routing algorithm.
type LoadBalanceStrategy int

const (
	StrategyLeastPending LoadBalanceStrategy = iota
	StrategyWeightedScore
	StrategyRoundRobin
	StrategyExpertAffinity
)

// MoELoadBalancer distributes requests across expert shard backends.
type MoELoadBalancer struct {
	backends  []*BackendState
	strategy  LoadBalanceStrategy
	rrCounter atomic.Int64
	mu        sync.RWMutex
}

func NewMoELoadBalancer(numShards int, numExperts int, strategy LoadBalanceStrategy) *MoELoadBalancer {
	expertsPerShard := int(math.Ceil(float64(numExperts) / float64(numShards)))
	backends := make([]*BackendState, numShards)
	for i := 0; i < numShards; i++ {
		start := i * expertsPerShard
		end := start + expertsPerShard
		if end > numExperts {
			end = numExperts
		}
		backends[i] = &BackendState{
			ShardID:     i,
			Host:        fmt.Sprintf("shard-%d", i),
			Port:        9000 + i,
			IsAlive:     true,
			ExpertRange: [2]int{start, end},
			Weight:      1.0,
			LastHealthy: time.Now(),
		}
	}
	return &MoELoadBalancer{
		backends: backends,
		strategy: strategy,
	}
}

// Select picks the best backend for a request targeting specific experts.
func (lb *MoELoadBalancer) Select(targetExperts []int) (*BackendState, error) {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	switch lb.strategy {
	case StrategyLeastPending:
		return lb.selectLeastPending()
	case StrategyWeightedScore:
		return lb.selectWeightedScore()
	case StrategyRoundRobin:
		return lb.selectRoundRobin()
	case StrategyExpertAffinity:
		return lb.selectExpertAffinity(targetExperts)
	default:
		return lb.selectLeastPending()
	}
}

func (lb *MoELoadBalancer) selectLeastPending() (*BackendState, error) {
	var best *BackendState
	var minPending int64 = math.MaxInt64
	for _, b := range lb.backends {
		if !b.IsAlive {
			continue
		}
		pending := b.PendingCount.Load()
		if pending < minPending {
			minPending = pending
			best = b
		}
	}
	if best == nil {
		return nil, fmt.Errorf("no healthy backends")
	}
	return best, nil
}

func (lb *MoELoadBalancer) selectWeightedScore() (*BackendState, error) {
	var best *BackendState
	bestScore := math.Inf(1)
	for _, b := range lb.backends {
		score := b.Score()
		if score < bestScore {
			bestScore = score
			best = b
		}
	}
	if best == nil {
		return nil, fmt.Errorf("no healthy backends")
	}
	return best, nil
}

func (lb *MoELoadBalancer) selectRoundRobin() (*BackendState, error) {
	n := int64(len(lb.backends))
	if n == 0 {
		return nil, fmt.Errorf("no backends")
	}
	for attempts := int64(0); attempts < n; attempts++ {
		idx := lb.rrCounter.Add(1) % n
		b := lb.backends[idx]
		if b.IsAlive {
			return b, nil
		}
	}
	return nil, fmt.Errorf("no healthy backends")
}

func (lb *MoELoadBalancer) selectExpertAffinity(targetExperts []int) (*BackendState, error) {
	if len(targetExperts) == 0 {
		return lb.selectLeastPending()
	}

	// Find shards that host the most target experts
	type shardScore struct {
		backend *BackendState
		matches int
	}
	scores := make([]shardScore, len(lb.backends))
	for i, b := range lb.backends {
		matches := 0
		for _, e := range targetExperts {
			if e >= b.ExpertRange[0] && e < b.ExpertRange[1] {
				matches++
			}
		}
		scores[i] = shardScore{backend: b, matches: matches}
	}

	// Pick the shard with most expert matches (tie-break by pending count)
	var best *BackendState
	bestMatches := -1
	var bestPending int64 = math.MaxInt64
	for _, s := range scores {
		if !s.backend.IsAlive {
			continue
		}
		pending := s.backend.PendingCount.Load()
		if s.matches > bestMatches || (s.matches == bestMatches && pending < bestPending) {
			best = s.backend
			bestMatches = s.matches
			bestPending = pending
		}
	}
	if best == nil {
		return nil, fmt.Errorf("no healthy backends for experts %v", targetExperts)
	}
	return best, nil
}

// HealthStatus returns the aggregate health of all backends.
func (lb *MoELoadBalancer) HealthStatus() map[string]interface{} {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	alive := 0
	totalPending := int64(0)
	totalCompleted := int64(0)
	for _, b := range lb.backends {
		if b.IsAlive {
			alive++
		}
		totalPending += b.PendingCount.Load()
		totalCompleted += b.CompletedCount.Load()
	}
	return map[string]interface{}{
		"total_backends":  len(lb.backends),
		"alive_backends":  alive,
		"total_pending":   totalPending,
		"total_completed": totalCompleted,
	}
}

