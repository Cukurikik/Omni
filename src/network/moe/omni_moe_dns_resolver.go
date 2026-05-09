package network_moe

import (
	"context"
	"fmt"
	"net"
	"sync"
	"time"
)

// OMNI MOTHER Production Zero-Mock Internal DNS Resolver
// Caches internal cluster IP resolutions to prevent DNS latency during
// high-throughput MoE Expert dispatches.

type DNSCacheEntry struct {
	IPs       []net.IP
	ExpiresAt time.Time
}

type OmniDNSResolver struct {
	mu    sync.RWMutex
	cache map[string]DNSCacheEntry
	ttl   time.Duration
}

func NewOmniDNSResolver(ttl time.Duration) *OmniDNSResolver {
	return &OmniDNSResolver{
		cache: make(map[string]DNSCacheEntry),
		ttl:   ttl,
	}
}

func (r *OmniDNSResolver) Resolve(ctx context.Context, hostname string) ([]net.IP, error) {
	// 1. Check Cache
	r.mu.RLock()
	entry, exists := r.cache[hostname]
	r.mu.RUnlock()

	if exists && time.Now().Before(entry.ExpiresAt) {
		return entry.IPs, nil
	}

	// 2. Cache Miss or Expired - Perform Lookup
	resolver := &net.Resolver{
		PreferGo: true,
	}

	ips, err := resolver.LookupIPAddr(ctx, hostname)
	if err != nil {
		return nil, fmt.Errorf("OMNI CRITICAL: DNS Resolution failed for %s: %v", hostname, err)
	}

	var parsedIPs []net.IP
	for _, ip := range ips {
		parsedIPs = append(parsedIPs, ip.IP)
	}

	// 3. Update Cache
	r.mu.Lock()
	r.cache[hostname] = DNSCacheEntry{
		IPs:       parsedIPs,
		ExpiresAt: time.Now().Add(r.ttl),
	}
	r.mu.Unlock()

	return parsedIPs, nil
}

