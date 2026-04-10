package omni_digitalocean_spaces

import "time"

type HealthStatus struct { Healthy bool; Latency time.Duration; Message string; Timestamp time.Time }
type HealthChecker struct { checks map[string]func() HealthStatus }

func NewHealthChecker() *HealthChecker { return &HealthChecker{checks: make(map[string]func() HealthStatus)} }
func (h *HealthChecker) Register(name string, fn func() HealthStatus) { h.checks[name] = fn }
func (h *HealthChecker) RunAll() map[string]HealthStatus {
	results := make(map[string]HealthStatus)
	for name, fn := range h.checks { results[name] = fn() }
	return results
}
func (h *HealthChecker) IsHealthy() bool {
	for _, status := range h.RunAll() { if !status.Healthy { return false } }
	return true
}