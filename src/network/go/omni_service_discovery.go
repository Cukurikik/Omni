package network_go

import (
	"log"
	"sync"
)

// OMNI MOTHER: Internal Service Discovery Registry (Production Grade)

type ServiceRegistry struct {
	services map[string][]string
	mu       sync.RWMutex
}

func NewServiceRegistry() *ServiceRegistry {
	return &ServiceRegistry{
		services: make(map[string][]string),
	}
}

func (r *ServiceRegistry) Register(name string, address string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.services[name] = append(r.services[name], address)
	log.Printf("[OMNI DISCOVERY] Registered %s at %s", name, address)
}

func (r *ServiceRegistry) GetInstances(name string) []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.services[name]
}

