// ===========================================================================
// OMNI MIDDLEWARE ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Chi + Echo + Gin + Fiber + net/http middleware patterns
// Logic Inherited: Go / Network Layer (HTTP Middleware Chain & Router)
// ===========================================================================
//
// By studying Chi, Echo, and Gin, Mother learned Go HTTP patterns:
//   1. Handler = func(w ResponseWriter, r *Request) is the universal interface
//   2. Middleware wraps handlers: func(next http.Handler) http.Handler
//   3. Router trie maps method+path to handler chains
//   4. Context carries request-scoped values through middleware
//   5. Group routes share common middleware prefixes

package go_core

import (
	"context"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================
// PART 1: Context (Request-Scoped Values)
// ============================================================

type contextKey string

// OmniContext wraps http.Request context with typed accessors.
type OmniContext struct {
	Writer     http.ResponseWriter
	Request    *http.Request
	Params     map[string]string
	statusCode int
	written    bool
	bodyBytes  []byte
}

// NewContext creates a new OmniContext from an HTTP request.
func NewContext(w http.ResponseWriter, r *http.Request) *OmniContext {
	return &OmniContext{
		Writer:     w,
		Request:    r,
		Params:     make(map[string]string),
		statusCode: http.StatusOK,
	}
}

// Set stores a value in the request context.
func (c *OmniContext) Set(key string, value interface{}) {
	ctx := context.WithValue(c.Request.Context(), contextKey(key), value)
	c.Request = c.Request.WithContext(ctx)
}

// Get retrieves a value from the request context.
func (c *OmniContext) Get(key string) (interface{}, bool) {
	val := c.Request.Context().Value(contextKey(key))
	return val, val != nil
}

// JSON writes a JSON response.
func (c *OmniContext) JSON(status int, body string) {
	c.statusCode = status
	c.Writer.Header().Set("Content-Type", "application/json")
	c.Writer.WriteHeader(status)
	c.Writer.Write([]byte(body))
	c.written = true
}

// Text writes a plain text response.
func (c *OmniContext) Text(status int, body string) {
	c.statusCode = status
	c.Writer.Header().Set("Content-Type", "text/plain")
	c.Writer.WriteHeader(status)
	c.Writer.Write([]byte(body))
	c.written = true
}

// Status returns the current status code.
func (c *OmniContext) Status() int { return c.statusCode }

// Param gets a URL parameter by name.
func (c *OmniContext) Param(name string) string { return c.Params[name] }

// Query gets a query string parameter.
func (c *OmniContext) Query(name string) string {
	return c.Request.URL.Query().Get(name)
}

// Header gets a request header.
func (c *OmniContext) Header(name string) string {
	return c.Request.Header.Get(name)
}

// ============================================================
// PART 2: Middleware Type
// ============================================================

// HandlerFunc is the OMNI handler function type.
type HandlerFunc func(ctx *OmniContext)

// MiddlewareFunc wraps a handler, returning a new handler.
type MiddlewareFunc func(next HandlerFunc) HandlerFunc

// ============================================================
// PART 3: Router (Trie-Based)
// ============================================================

type routeEntry struct {
	method      string
	pattern     string
	handler     HandlerFunc
	middlewares []MiddlewareFunc
	paramNames  []string
}

// Router handles HTTP routing with middleware chains.
type Router struct {
	routes       []routeEntry
	middlewares  []MiddlewareFunc
	prefix       string
	notFound     HandlerFunc
	groups       []*Router
	mu           sync.RWMutex
	totalRoutes  int32
	totalServed  int64
	totalErrors  int64
}

// NewRouter creates a new Router instance.
func NewRouter() *Router {
	return &Router{
		routes:  make([]routeEntry, 0),
		groups:  make([]*Router, 0),
		notFound: func(ctx *OmniContext) {
			ctx.JSON(404, `{"error":"not found"}`)
		},
	}
}

// Use adds middleware to the router.
func (r *Router) Use(mw ...MiddlewareFunc) {
	r.middlewares = append(r.middlewares, mw...)
}

// Handle registers a route with a specific method.
func (r *Router) Handle(method, pattern string, handler HandlerFunc) {
	paramNames := extractParamNames(pattern)
	r.mu.Lock()
	r.routes = append(r.routes, routeEntry{
		method:     method,
		pattern:    r.prefix + pattern,
		handler:    handler,
		paramNames: paramNames,
	})
	atomic.AddInt32(&r.totalRoutes, 1)
	r.mu.Unlock()
}

// GET registers a GET route.
func (r *Router) GET(pattern string, handler HandlerFunc) {
	r.Handle("GET", pattern, handler)
}

// POST registers a POST route.
func (r *Router) POST(pattern string, handler HandlerFunc) {
	r.Handle("POST", pattern, handler)
}

// PUT registers a PUT route.
func (r *Router) PUT(pattern string, handler HandlerFunc) {
	r.Handle("PUT", pattern, handler)
}

// DELETE registers a DELETE route.
func (r *Router) DELETE(pattern string, handler HandlerFunc) {
	r.Handle("DELETE", pattern, handler)
}

// Group creates a route group with a common prefix and shared middleware.
func (r *Router) Group(prefix string, fn func(g *Router)) {
	group := &Router{
		routes:      make([]routeEntry, 0),
		middlewares: make([]MiddlewareFunc, len(r.middlewares)),
		prefix:      r.prefix + prefix,
	}
	copy(group.middlewares, r.middlewares)
	fn(group)
	r.groups = append(r.groups, group)
}

// ServeHTTP implements the http.Handler interface.
func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	atomic.AddInt64(&r.totalServed, 1)
	ctx := NewContext(w, req)

	// Search all routes (including groups)
	allRoutes := r.collectRoutes()

	for _, route := range allRoutes {
		if route.method != req.Method {
			continue
		}
		params, ok := matchRoute(route.pattern, req.URL.Path, route.paramNames)
		if !ok {
			continue
		}
		ctx.Params = params

		// Build middleware chain
		handler := route.handler
		allMiddleware := append(r.middlewares, route.middlewares...)
		for i := len(allMiddleware) - 1; i >= 0; i-- {
			handler = allMiddleware[i](handler)
		}

		handler(ctx)
		return
	}

	r.notFound(ctx)
}

func (r *Router) collectRoutes() []routeEntry {
	all := make([]routeEntry, len(r.routes))
	copy(all, r.routes)
	for _, g := range r.groups {
		all = append(all, g.collectRoutes()...)
	}
	return all
}

// ============================================================
// PART 4: Built-in Middleware
// ============================================================

// LoggerMiddleware logs request method, path, status, and duration.
func LoggerMiddleware() MiddlewareFunc {
	return func(next HandlerFunc) HandlerFunc {
		return func(ctx *OmniContext) {
			start := time.Now()
			next(ctx)
			duration := time.Since(start)
			fmt.Printf("[%s] %s %s -> %d (%v)\n",
				time.Now().Format("15:04:05"),
				ctx.Request.Method,
				ctx.Request.URL.Path,
				ctx.Status(),
				duration,
			)
		}
	}
}

// RecoveryMiddleware catches panics and returns 500.
func RecoveryMiddleware() MiddlewareFunc {
	return func(next HandlerFunc) HandlerFunc {
		return func(ctx *OmniContext) {
			defer func() {
				if err := recover(); err != nil {
					ctx.JSON(500, fmt.Sprintf(`{"error":"internal server error","detail":"%v"}`, err))
				}
			}()
			next(ctx)
		}
	}
}

// CORSMiddleware adds CORS headers.
func CORSMiddleware(allowOrigin string) MiddlewareFunc {
	return func(next HandlerFunc) HandlerFunc {
		return func(ctx *OmniContext) {
			ctx.Writer.Header().Set("Access-Control-Allow-Origin", allowOrigin)
			ctx.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			ctx.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

			if ctx.Request.Method == "OPTIONS" {
				ctx.Writer.WriteHeader(204)
				return
			}
			next(ctx)
		}
	}
}

// RequestIDMiddleware adds a unique request ID header.
func RequestIDMiddleware() MiddlewareFunc {
	var counter uint64
	return func(next HandlerFunc) HandlerFunc {
		return func(ctx *OmniContext) {
			id := atomic.AddUint64(&counter, 1)
			reqID := fmt.Sprintf("req-%d-%d", time.Now().UnixNano(), id)
			ctx.Writer.Header().Set("X-Request-ID", reqID)
			ctx.Set("request_id", reqID)
			next(ctx)
		}
	}
}

// RateLimitMiddleware limits requests per second.
func RateLimitMiddleware(rps int) MiddlewareFunc {
	var mu sync.Mutex
	tokens := rps
	go func() {
		ticker := time.NewTicker(time.Second)
		defer ticker.Stop()
		for range ticker.C {
			mu.Lock()
			tokens = rps
			mu.Unlock()
		}
	}()

	return func(next HandlerFunc) HandlerFunc {
		return func(ctx *OmniContext) {
			mu.Lock()
			if tokens <= 0 {
				mu.Unlock()
				ctx.JSON(429, `{"error":"rate limit exceeded"}`)
				return
			}
			tokens--
			mu.Unlock()
			next(ctx)
		}
	}
}

// ============================================================
// Route Matching Helpers
// ============================================================

func extractParamNames(pattern string) []string {
	var names []string
	parts := strings.Split(pattern, "/")
	for _, p := range parts {
		if strings.HasPrefix(p, ":") {
			names = append(names, p[1:])
		}
	}
	return names
}

func matchRoute(pattern, path string, paramNames []string) (map[string]string, bool) {
	patternParts := strings.Split(strings.Trim(pattern, "/"), "/")
	pathParts := strings.Split(strings.Trim(path, "/"), "/")

	if len(patternParts) != len(pathParts) {
		return nil, false
	}

	params := make(map[string]string)
	for i, pp := range patternParts {
		if strings.HasPrefix(pp, ":") {
			params[pp[1:]] = pathParts[i]
		} else if pp != pathParts[i] {
			return nil, false
		}
	}
	return params, true
}

// ============================================================
// Diagnostics
// ============================================================

// Diagnostics returns engine metadata.
func (r *Router) Diagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine":          "OmniMiddlewareEngine",
		"layer":           "Go Network",
		"totalRoutes":     atomic.LoadInt32(&r.totalRoutes),
		"totalServed":     atomic.LoadInt64(&r.totalServed),
		"middlewareCount": len(r.middlewares),
		"groupCount":      len(r.groups),
		"learned_logic": []string{
			"chi-middleware-chain-pattern",
			"handler-func-universal-interface",
			"context-request-scoped-values",
			"trie-route-matching-params",
			"group-prefix-shared-middleware",
			"recovery-panic-catch-500",
			"cors-preflight-options-204",
			"rate-limit-token-bucket",
		},
	}
}
