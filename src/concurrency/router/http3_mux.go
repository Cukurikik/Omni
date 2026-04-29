package router

import (
	"net/http"
	"sync"
)

type RouteHandler func(ctx context.Context, req *http.Request) (interface{}, error)

type OmniHttp3Mux struct {
	routes map[string]RouteHandler
	mu     sync.RWMutex
}

func NewOmniHttp3Mux() *OmniHttp3Mux {
	return &OmniHttp3Mux{
		routes: make(map[string]RouteHandler),
	}
}

func (m *OmniHttp3Mux) Handle(path string, handler RouteHandler) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if _, exists := m.routes[path]; exists {
		return errors.New("route already exists: " + path)
	}
	m.routes[path] = handler
	return nil
}

func (m *OmniHttp3Mux) Dispatch(ctx context.Context, path string, req *http.Request) (interface{}, error) {
	m.mu.RLock()
	handler, exists := m.routes[path]
	m.mu.RUnlock()
	
	if !exists {
		return nil, errors.New("route not found")
	}
	
	return handler(ctx, req)
}
