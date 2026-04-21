// ===========================================================================
// OMNI NETWORK LAYER — GATEWAY HTTP/3 ROUTER
// ===========================================================================
// Domain Layer   : Network (Green threads, channel-based CSP, HTTP server)
// Language        : Go
// Function        : High-performance API gateway with multi-layer routing,
//                   middleware chain (auth, rate-limit, CORS, logging),
//                   request/response transformation, and health endpoints
// ===========================================================================

package network

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

// ---- Middleware Types ------------------------------------------------------

type RequestContext struct {
	Method      string
	Path        string
	Headers     map[string]string
	Body        []byte
	RemoteAddr  string
	StartedAt   time.Time
	RouteParams map[string]string
	UserID      string // set by auth middleware
}

type ResponseContext struct {
	StatusCode  int
	Headers     map[string]string
	Body        []byte
	ContentType string
}

type MiddlewareFn func(ctx *RequestContext) (*ResponseContext, error)
type HandlerFn func(ctx *RequestContext) *ResponseContext

// ---- Route Definition -----------------------------------------------------

type Route struct {
	Method     string
	Pattern    string
	Handler    HandlerFn
	Middleware []MiddlewareFn
}

// ---- Gateway Router -------------------------------------------------------

type OmniGateway struct {
	routes        []Route
	globalMiddleware []MiddlewareFn
	mu            sync.RWMutex
	requestCount  uint64
	errorCount    uint64
	startedAt     time.Time
}

func NewOmniGateway() *OmniGateway {
	fmt.Println("[GATEWAY-OMNI-GO] API Gateway initialized.")
	return &OmniGateway{
		startedAt: time.Now(),
	}
}

// Use adds global middleware applied to ALL routes.
func (g *OmniGateway) Use(mw MiddlewareFn) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.globalMiddleware = append(g.globalMiddleware, mw)
}

// Route registers a new route with optional route-specific middleware.
func (g *OmniGateway) Route(method, pattern string, handler HandlerFn, middleware ...MiddlewareFn) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.routes = append(g.routes, Route{
		Method:     strings.ToUpper(method),
		Pattern:    pattern,
		Handler:    handler,
		Middleware: middleware,
	})
	fmt.Printf("[GATEWAY-OMNI-GO] Route: %s %s (%d middleware)\n", method, pattern, len(middleware))
}

// GET/POST/PUT/DELETE convenience methods.
func (g *OmniGateway) GET(pattern string, h HandlerFn, mw ...MiddlewareFn)    { g.Route("GET", pattern, h, mw...) }
func (g *OmniGateway) POST(pattern string, h HandlerFn, mw ...MiddlewareFn)   { g.Route("POST", pattern, h, mw...) }
func (g *OmniGateway) PUT(pattern string, h HandlerFn, mw ...MiddlewareFn)    { g.Route("PUT", pattern, h, mw...) }
func (g *OmniGateway) DELETE(pattern string, h HandlerFn, mw ...MiddlewareFn) { g.Route("DELETE", pattern, h, mw...) }

// HandleRequest processes an incoming request through the middleware chain.
func (g *OmniGateway) HandleRequest(ctx *RequestContext) *ResponseContext {
	g.mu.RLock()
	defer g.mu.RUnlock()
	g.requestCount++
	ctx.StartedAt = time.Now()

	// Match route
	var matched *Route
	for i := range g.routes {
		if g.routes[i].Method == ctx.Method && matchPattern(g.routes[i].Pattern, ctx.Path, ctx) {
			matched = &g.routes[i]
			break
		}
	}

	if matched == nil {
		g.errorCount++
		return &ResponseContext{StatusCode: 404, Body: []byte(`{"error":"route not found"}`), ContentType: "application/json"}
	}

	// Execute global middleware
	for _, mw := range g.globalMiddleware {
		resp, err := mw(ctx)
		if err != nil || resp != nil {
			if resp != nil { return resp }
			g.errorCount++
			return &ResponseContext{StatusCode: 500, Body: []byte(err.Error())}
		}
	}

	// Execute route-specific middleware
	for _, mw := range matched.Middleware {
		resp, err := mw(ctx)
		if err != nil || resp != nil {
			if resp != nil { return resp }
			g.errorCount++
			return &ResponseContext{StatusCode: 500, Body: []byte(err.Error())}
		}
	}

	// Execute handler
	return matched.Handler(ctx)
}

// ---- Built-in Middleware --------------------------------------------------

// LoggingMiddleware logs request method, path, and duration.
func LoggingMiddleware() MiddlewareFn {
	return func(ctx *RequestContext) (*ResponseContext, error) {
		fmt.Printf("[GATEWAY-OMNI-GO] %s %s from %s\n", ctx.Method, ctx.Path, ctx.RemoteAddr)
		return nil, nil // pass through
	}
}

// CORSMiddleware adds CORS headers.
func CORSMiddleware(allowedOrigins string) MiddlewareFn {
	return func(ctx *RequestContext) (*ResponseContext, error) {
		if ctx.Method == "OPTIONS" {
			return &ResponseContext{
				StatusCode: 204,
				Headers: map[string]string{
					"Access-Control-Allow-Origin":  allowedOrigins,
					"Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
					"Access-Control-Allow-Headers": "Content-Type,Authorization",
				},
			}, nil
		}
		return nil, nil
	}
}

// RateLimitMiddleware applies per-IP rate limiting.
func RateLimitMiddleware(maxPerMinute int) MiddlewareFn {
	counters := make(map[string]int)
	var mu sync.Mutex
	go func() {
		for range time.Tick(time.Minute) {
			mu.Lock()
			counters = make(map[string]int)
			mu.Unlock()
		}
	}()

	return func(ctx *RequestContext) (*ResponseContext, error) {
		mu.Lock()
		counters[ctx.RemoteAddr]++
		count := counters[ctx.RemoteAddr]
		mu.Unlock()

		if count > maxPerMinute {
			return &ResponseContext{
				StatusCode: 429,
				Body:       []byte(`{"error":"rate limit exceeded"}`),
				ContentType: "application/json",
			}, nil
		}
		return nil, nil
	}
}

// ---- Health Endpoint ------------------------------------------------------

func (g *OmniGateway) HealthHandler() HandlerFn {
	return func(ctx *RequestContext) *ResponseContext {
		uptime := time.Since(g.startedAt).Seconds()
		body := fmt.Sprintf(`{"status":"healthy","routes":%d,"requests":%d,"errors":%d,"uptime":"%.0fs"}`,
			len(g.routes), g.requestCount, g.errorCount, uptime)
		return &ResponseContext{StatusCode: 200, Body: []byte(body), ContentType: "application/json"}
	}
}

// ---- Pattern Matching (simple, supports :param) ---------------------------

func matchPattern(pattern, path string, ctx *RequestContext) bool {
	patParts := strings.Split(pattern, "/")
	pathParts := strings.Split(path, "/")
	if len(patParts) != len(pathParts) { return false }

	for i, pp := range patParts {
		if strings.HasPrefix(pp, ":") {
			if ctx.RouteParams == nil { ctx.RouteParams = make(map[string]string) }
			ctx.RouteParams[pp[1:]] = pathParts[i]
		} else if pp != pathParts[i] {
			return false
		}
	}
	return true
}
