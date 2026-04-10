package omni_cloudflare_workers

import "sync"

type ServiceEndpoint struct { Host string; Port int; Weight int; Healthy bool }
type ServiceRegistry struct { mu sync.RWMutex; services map[string][]ServiceEndpoint }

func NewServiceRegistry() *ServiceRegistry { return &ServiceRegistry{services: make(map[string][]ServiceEndpoint)} }
func (r *ServiceRegistry) Register(name string, ep ServiceEndpoint) {
	r.mu.Lock(); defer r.mu.Unlock()
	r.services[name] = append(r.services[name], ep)
}
func (r *ServiceRegistry) Lookup(name string) []ServiceEndpoint {
	r.mu.RLock(); defer r.mu.RUnlock()
	return r.services[name]
}
func (r *ServiceRegistry) Deregister(name string) {
	r.mu.Lock(); defer r.mu.Unlock()
	delete(r.services, name)
}