// Omni LLM7 Gateway Router (Go)
// Network Layer: Multi-provider LLM API gateway routing.
// Ref: chigwell/llm7.io — Single API gateway for AI models.
package network_gocore

import (
	"errors"
	"strings"
	"sync/atomic"
)

type ProviderConfig struct {
	Name     string
	Endpoint string
	Weight   int
}
type Gateway struct {
	providers []ProviderConfig
	counter   uint64
}

func NewGateway(providers []ProviderConfig) *Gateway { return &Gateway{providers: providers} }
func (g *Gateway) Route(model string) (*ProviderConfig, error) {
	if len(g.providers) == 0 {
		return nil, errors.New("OMNI_ERR: no providers")
	}
	for _, p := range g.providers {
		if strings.Contains(strings.ToLower(model), strings.ToLower(p.Name)) {
			atomic.AddUint64(&g.counter, 1)
			return &p, nil
		}
	}
	idx := atomic.AddUint64(&g.counter, 1) % uint64(len(g.providers))
	return &g.providers[idx], nil
}

