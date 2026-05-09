// Omni AgentWatch Telemetry Proxy (Go)
// Ref: cyberark/agentwatch — Apache-2.0
package network_gocore

import (
	"errors"
	"sync"
	"time"
)

type TraceEvent struct {
	AgentID   string
	Action    string
	LatencyMs float64
	Tokens    int
	Ts        int64
}
type Collector struct {
	mu     sync.Mutex
	events []TraceEvent
}

func NewCollector() *Collector { return &Collector{} }
func (c *Collector) Record(agentID, action string, latencyMs float64, tokens int) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.events = append(c.events, TraceEvent{agentID, action, latencyMs, tokens, time.Now().UnixMilli()})
}
func (c *Collector) Stats() (int, float64, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if len(c.events) == 0 {
		return 0, 0, errors.New("OMNI_ERR: no events")
	}
	total := 0.0
	for _, e := range c.events {
		total += e.LatencyMs
	}
	return len(c.events), total / float64(len(c.events)), nil
}

