package network_go

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// OMNI MOTHER: gRPC-REST Gateway (Production Grade)
// Translates REST JSON requests into gRPC-like internal calls.
// Supports path routing, middleware pipeline, and health checks.

type HandlerFunc func(ctx context.Context, req *GatewayRequest) (*GatewayResponse, error)

type GatewayRequest struct {
	Method  string
	Path    string
	Headers map[string]string
	Body    json.RawMessage
	Params  map[string]string
}

type GatewayResponse struct {
	StatusCode int
	Headers    map[string]string
	Body       interface{}
}

type MiddlewareFunc func(HandlerFunc) HandlerFunc

type Route struct {
	Method  string
	Pattern string
	Handler HandlerFunc
}

type OmniGateway struct {
	mu          sync.RWMutex
	routes      []Route
	middlewares []MiddlewareFunc
	server      *http.Server
	reqCount    int64
	errCount    int64
}

func NewOmniGateway() *OmniGateway {
	return &OmniGateway{
		routes:      make([]Route, 0),
		middlewares: make([]MiddlewareFunc, 0),
	}
}

func (g *OmniGateway) Use(mw MiddlewareFunc) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.middlewares = append(g.middlewares, mw)
}

func (g *OmniGateway) Register(method, pattern string, h HandlerFunc) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.routes = append(g.routes, Route{Method: method, Pattern: pattern, Handler: h})
	log.Printf("[OMNI GW] Registered %s %s", method, pattern)
}

func (g *OmniGateway) matchRoute(method, path string) (HandlerFunc, map[string]string) {
	g.mu.RLock()
	defer g.mu.RUnlock()

	for _, r := range g.routes {
		if r.Method != method {
			continue
		}
		params := matchPattern(r.Pattern, path)
		if params != nil {
			return r.Handler, params
		}
	}
	return nil, nil
}

func matchPattern(pattern, path string) map[string]string {
	pp := strings.Split(strings.Trim(pattern, "/"), "/")
	ap := strings.Split(strings.Trim(path, "/"), "/")
	if len(pp) != len(ap) {
		return nil
	}
	params := make(map[string]string)
	for i, seg := range pp {
		if strings.HasPrefix(seg, ":") {
			params[seg[1:]] = ap[i]
		} else if seg != ap[i] {
			return nil
		}
	}
	return params
}

func (g *OmniGateway) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	atomic.AddInt64(&g.reqCount, 1)
	start := time.Now()

	handler, params := g.matchRoute(r.Method, r.URL.Path)
	if handler == nil {
		// Health check
		if r.URL.Path == "/healthz" {
			w.WriteHeader(200)
			json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
			return
		}
		w.WriteHeader(404)
		json.NewEncoder(w).Encode(map[string]string{"error": "not found"})
		return
	}

	// Apply middleware chain
	finalHandler := handler
	for i := len(g.middlewares) - 1; i >= 0; i-- {
		finalHandler = g.middlewares[i](finalHandler)
	}

	// Build request
	headers := make(map[string]string)
	for k, vals := range r.Header {
		headers[k] = vals[0]
	}

	var body json.RawMessage
	if r.Body != nil {
		defer r.Body.Close()
		json.NewDecoder(r.Body).Decode(&body)
	}

	req := &GatewayRequest{
		Method:  r.Method,
		Path:    r.URL.Path,
		Headers: headers,
		Body:    body,
		Params:  params,
	}

	resp, err := finalHandler(r.Context(), req)
	if err != nil {
		atomic.AddInt64(&g.errCount, 1)
		w.WriteHeader(500)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		log.Printf("[OMNI GW] ERROR %s %s: %v (%v)", r.Method, r.URL.Path, err, time.Since(start))
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if resp.Headers != nil {
		for k, v := range resp.Headers {
			w.Header().Set(k, v)
		}
	}
	w.WriteHeader(resp.StatusCode)
	json.NewEncoder(w).Encode(resp.Body)

	log.Printf("[OMNI GW] %s %s → %d (%v)", r.Method, r.URL.Path, resp.StatusCode, time.Since(start))
}

func (g *OmniGateway) ListenAndServe(addr string, tlsConfig *tls.Config) error {
	g.server = &http.Server{
		Addr:         addr,
		Handler:      g,
		TLSConfig:    tlsConfig,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	log.Printf("[OMNI GW] Listening on %s", addr)
	return g.server.ListenAndServe()
}

func (g *OmniGateway) Shutdown(ctx context.Context) error {
	if g.server != nil {
		return g.server.Shutdown(ctx)
	}
	return nil
}

func (g *OmniGateway) Stats() map[string]interface{} {
	return map[string]interface{}{
		"total_requests": atomic.LoadInt64(&g.reqCount),
		"total_errors":   atomic.LoadInt64(&g.errCount),
		"routes":         len(g.routes),
	}
}

// ---- Built-in Middleware ----

func LoggingMiddleware(next HandlerFunc) HandlerFunc {
	return func(ctx context.Context, req *GatewayRequest) (*GatewayResponse, error) {
		start := time.Now()
		resp, err := next(ctx, req)
		log.Printf("[OMNI MW] %s %s → %v (%v)", req.Method, req.Path, err, time.Since(start))
		return resp, err
	}
}

func CORSMiddleware(next HandlerFunc) HandlerFunc {
	return func(ctx context.Context, req *GatewayRequest) (*GatewayResponse, error) {
		resp, err := next(ctx, req)
		if resp != nil {
			if resp.Headers == nil {
				resp.Headers = make(map[string]string)
			}
			resp.Headers["Access-Control-Allow-Origin"] = "*"
			resp.Headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
		}
		return resp, err
	}
}

func RecoveryMiddleware(next HandlerFunc) HandlerFunc {
	return func(ctx context.Context, req *GatewayRequest) (resp *GatewayResponse, err error) {
		defer func() {
			if r := recover(); r != nil {
				log.Printf("[OMNI MW] Panic recovered: %v", r)
				err = fmt.Errorf("internal server error: %v", r)
				resp = &GatewayResponse{StatusCode: 500, Body: map[string]string{"error": "internal error"}}
			}
		}()
		return next(ctx, req)
	}
}

