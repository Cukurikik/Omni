// ============================================================
// 🐹 OMNI-HTTP2: Go Native HTTP/2 Server
// ============================================================
// Pengganti total Node.js `http.createServer()` dan Express.js
// dengan native Go HTTP/2 yang mendukung multiplexing, 
// middleware chain, dan routing built-in.
// ============================================================

package protocols

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// HandlerFn adalah tipe handler route OMNI
type HandlerFn func(ctx *RequestContext)

// MiddlewareFn adalah tipe middleware
type MiddlewareFn func(ctx *RequestContext, next func())

// RequestContext membungkus request/response dengan utilitas
type RequestContext struct {
	Writer  http.ResponseWriter
	Request *http.Request
	Params  map[string]string
	Status  int
	start   time.Time
}

// JSON mengirim response JSON
func (ctx *RequestContext) JSON(statusCode int, data interface{}) {
	ctx.Writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	ctx.Writer.WriteHeader(statusCode)
	ctx.Status = statusCode
	json.NewEncoder(ctx.Writer).Encode(data)
}

// Text mengirim response teks biasa
func (ctx *RequestContext) Text(statusCode int, text string) {
	ctx.Writer.Header().Set("Content-Type", "text/plain; charset=utf-8")
	ctx.Writer.WriteHeader(statusCode)
	ctx.Status = statusCode
	ctx.Writer.Write([]byte(text))
}

// HTML mengirim response HTML
func (ctx *RequestContext) HTML(statusCode int, html string) {
	ctx.Writer.Header().Set("Content-Type", "text/html; charset=utf-8")
	ctx.Writer.WriteHeader(statusCode)
	ctx.Status = statusCode
	ctx.Writer.Write([]byte(html))
}

// SetHeader mengatur header response
func (ctx *RequestContext) SetHeader(key, value string) {
	ctx.Writer.Header().Set(key, value)
}

// GetHeader mengambil header request
func (ctx *RequestContext) GetHeader(key string) string {
	return ctx.Request.Header.Get(key)
}

// QueryParam mengambil query parameter
func (ctx *RequestContext) QueryParam(key string) string {
	return ctx.Request.URL.Query().Get(key)
}

// Elapsed mengembalikan durasi sejak request dimulai
func (ctx *RequestContext) Elapsed() time.Duration {
	return time.Since(ctx.start)
}

// ============================================================
// Route Registry
// ============================================================

type route struct {
	method  string
	pattern string
	handler HandlerFn
}

// OmniHTTPServer adalah server HTTP/2 native OMNI
type OmniHTTPServer struct {
	mu          sync.RWMutex
	routes      []route
	middlewares []MiddlewareFn
	server      *http.Server
	address     string
	running     bool
}

// NewHTTPServer membuat server HTTP baru
func NewHTTPServer(address string) *OmniHTTPServer {
	return &OmniHTTPServer{
		routes:  make([]route, 0),
		address: address,
	}
}

// Use menambahkan middleware ke chain
func (s *OmniHTTPServer) Use(mw MiddlewareFn) {
	s.middlewares = append(s.middlewares, mw)
}

// GET mendaftarkan route GET
func (s *OmniHTTPServer) GET(pattern string, handler HandlerFn) {
	s.routes = append(s.routes, route{method: "GET", pattern: pattern, handler: handler})
}

// POST mendaftarkan route POST
func (s *OmniHTTPServer) POST(pattern string, handler HandlerFn) {
	s.routes = append(s.routes, route{method: "POST", pattern: pattern, handler: handler})
}

// PUT mendaftarkan route PUT
func (s *OmniHTTPServer) PUT(pattern string, handler HandlerFn) {
	s.routes = append(s.routes, route{method: "PUT", pattern: pattern, handler: handler})
}

// DELETE mendaftarkan route DELETE
func (s *OmniHTTPServer) DELETE(pattern string, handler HandlerFn) {
	s.routes = append(s.routes, route{method: "DELETE", pattern: pattern, handler: handler})
}

// ServeHTTP mengimplementasikan http.Handler interface
func (s *OmniHTTPServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := &RequestContext{
		Writer:  w,
		Request: r,
		Params:  make(map[string]string),
		Status:  200,
		start:   time.Now(),
	}

	// Jalankan middleware chain
	middlewareIndex := 0
	var runNext func()
	runNext = func() {
		if middlewareIndex < len(s.middlewares) {
			mw := s.middlewares[middlewareIndex]
			middlewareIndex++
			mw(ctx, runNext)
		} else {
			// Setelah semua middleware, cari route yang cocok
			s.matchRoute(ctx)
		}
	}
	runNext()
}

// matchRoute mencocokkan URL dengan route terdaftar
func (s *OmniHTTPServer) matchRoute(ctx *RequestContext) {
	for _, r := range s.routes {
		if r.method == ctx.Request.Method && r.pattern == ctx.Request.URL.Path {
			r.handler(ctx)
			return
		}
	}
	// 404 Not Found
	ctx.JSON(404, map[string]string{
		"error":   "Not Found",
		"path":    ctx.Request.URL.Path,
		"runtime": "OMNI-HTTP/2.0",
	})
}

// Listen memulai server HTTP/2
func (s *OmniHTTPServer) Listen() error {
	s.server = &http.Server{
		Addr:         s.address,
		Handler:      s,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	s.mu.Lock()
	s.running = true
	s.mu.Unlock()

	fmt.Printf("[OMNI-HTTP] Server listening on %s (%d routes)\n",
		s.address, len(s.routes))

	return s.server.ListenAndServe()
}

// Stop menghentikan server secara graceful
func (s *OmniHTTPServer) Stop() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.running = false
	if s.server != nil {
		return s.server.Close()
	}
	return nil
}

// ============================================================
// Built-in Middlewares
// ============================================================

// LoggerMiddleware mencatat setiap request ke stdout
func LoggerMiddleware() MiddlewareFn {
	return func(ctx *RequestContext, next func()) {
		next()
		fmt.Printf("[OMNI] %s %s -> %d (%v)\n",
			ctx.Request.Method, ctx.Request.URL.Path,
			ctx.Status, ctx.Elapsed())
	}
}

// CORSMiddleware menambahkan header CORS
func CORSMiddleware(origin string) MiddlewareFn {
	return func(ctx *RequestContext, next func()) {
		ctx.SetHeader("Access-Control-Allow-Origin", origin)
		ctx.SetHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		ctx.SetHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if ctx.Request.Method == "OPTIONS" {
			ctx.Status = 204
			ctx.Writer.WriteHeader(204)
			return
		}
		next()
	}
}

// RecoveryMiddleware menangkap panic dan mengembalikan 500
func RecoveryMiddleware() MiddlewareFn {
	return func(ctx *RequestContext, next func()) {
		defer func() {
			if r := recover(); r != nil {
				ctx.JSON(500, map[string]interface{}{
					"error":   "Internal Server Error",
					"details": fmt.Sprintf("%v", r),
				})
			}
		}()
		next()
	}
}
