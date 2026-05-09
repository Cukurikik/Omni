// Omni AI Gateway Router (Go)
// Network Layer: Load-balanced multi-provider LLM gateway routing.
// Ref: missingstudio/gateway — AI Gateway infrastructure.

package network_gocore

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sync/atomic"
)

type Provider struct {
	Name     string
	Endpoint string
	Weight   int32
}

type GatewayRouter struct {
	providers []Provider
	counter   uint64
}

func NewGatewayRouter(providers []Provider) (*GatewayRouter, error) {
	if len(providers) == 0 {
		return nil, errors.New("at least one provider required")
	}
	return &GatewayRouter{providers: providers}, nil
}

func (r *GatewayRouter) Route() Provider {
	idx := atomic.AddUint64(&r.counter, 1)
	return r.providers[idx%uint64(len(r.providers))]
}

func ComputeRequestHash(payload []byte) string {
	h := sha256.Sum256(payload)
	return hex.EncodeToString(h[:8])
}

