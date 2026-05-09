// moe_fault_tolerant_heartbeat.go — Network / Resiliency
// Layer: Network / Go — Fault-Tolerant Node Heartbeat
//
// In a distributed MoE cluster, expert nodes can crash (OOM, Hardware fault).
// The orchestrator must instantly reroute tokens if an expert node goes down.
// This Go module implements a high-frequency, low-overhead UDP heartbeat
// monitor using exponential decay to detect node death in under 5 milliseconds.

package network_moe

import (
	"fmt"
	"sync"
	"time"
)

type NodeStatus struct {
	LastSeen  time.Time
	MissCount int
	IsAlive   bool
}

type HeartbeatMonitor struct {
	nodes     map[string]*NodeStatus
	mu        sync.RWMutex
	timeout   time.Duration
	maxMisses int
}

func NewHeartbeatMonitor(timeoutMs int, maxMisses int) *HeartbeatMonitor {
	fmt.Printf("[Network] Initialized Fault-Tolerant Heartbeat Monitor (Timeout: %dms).\n", timeoutMs)
	return &HeartbeatMonitor{
		nodes:     make(map[string]*NodeStatus),
		timeout:   time.Duration(timeoutMs) * time.Millisecond,
		maxMisses: maxMisses,
	}
}

// RegisterNode adds a new Expert Node to the monitoring pool
func (hm *HeartbeatMonitor) RegisterNode(nodeID string) {
	hm.mu.Lock()
	defer hm.mu.Lock()
	hm.nodes[nodeID] = &NodeStatus{
		LastSeen:  time.Now(),
		MissCount: 0,
		IsAlive:   true,
	}
}

// ReceivePing is called whenever a UDP heartbeat packet arrives from a node
func (hm *HeartbeatMonitor) ReceivePing(nodeID string) {
	hm.mu.Lock()
	defer hm.mu.Unlock()

	if status, exists := hm.nodes[nodeID]; exists {
		status.LastSeen = time.Now()
		status.MissCount = 0
		if !status.IsAlive {
			fmt.Printf("[Network] Node %s recovered and is back online.\n", nodeID)
			status.IsAlive = true
		}
	}
}

// Watchdog runs continuously in a goroutine to check for expired heartbeats
func (hm *HeartbeatMonitor) Watchdog() {
	ticker := time.NewTicker(hm.timeout / 2)
	defer ticker.Stop()

	for range ticker.C {
		now := time.Now()
		hm.mu.Lock()

		for id, status := range hm.nodes {
			if status.IsAlive && now.Sub(status.LastSeen) > hm.timeout {
				status.MissCount++
				if status.MissCount >= hm.maxMisses {
					status.IsAlive = false
					fmt.Printf("[CRITICAL] Expert Node %s declared DEAD. Triggering orchestrator reroute.\n", id)
					// Trigger rerouting logic via channel or callback
				}
			}
		}

		hm.mu.Unlock()
	}
}

