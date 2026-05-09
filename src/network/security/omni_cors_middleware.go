package security

// omni_cors_middleware.go — Strict CORS Configuration
// Layer: Network / Go
//
// Implements Cross-Origin Resource Sharing (CORS) rules.
// Enforces strict allowed origins, methods, and credentials handling. Zero mock.

import (
	"net/http"
	"strings"
)

type CORSOptions struct {
	AllowedOrigins   []string
	AllowedMethods   []string
	AllowedHeaders   []string
	ExposedHeaders   []string
	AllowCredentials bool
	MaxAge           int // In seconds
}

// OmniCORSMiddleware wraps an http.Handler with strictly enforced CORS headers.
func OmniCORSMiddleware(options CORSOptions, next http.Handler) http.Handler {

	// Pre-join string slices to avoid doing it on every request
	allowedMethodsStr := strings.Join(options.AllowedMethods, ", ")
	allowedHeadersStr := strings.Join(options.AllowedHeaders, ", ")
	exposedHeadersStr := strings.Join(options.ExposedHeaders, ", ")

	// Helper to check if origin is allowed
	isOriginAllowed := func(origin string) bool {
		for _, o := range options.AllowedOrigins {
			if o == "*" || o == origin {
				return true
			}
		}
		return false
	}

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")

		// If no origin, it's not a CORS request (e.g., direct server-to-server)
		if origin == "" {
			next.ServeHTTP(w, r)
			return
		}

		if isOriginAllowed(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)

			if options.AllowCredentials {
				w.Header().Set("Access-Control-Allow-Credentials", "true")
			}

			if exposedHeadersStr != "" {
				w.Header().Set("Access-Control-Expose-Headers", exposedHeadersStr)
			}
		}

		// Handle Preflight (OPTIONS) requests
		if r.Method == http.MethodOptions {
			w.Header().Set("Access-Control-Allow-Methods", allowedMethodsStr)
			w.Header().Set("Access-Control-Allow-Headers", allowedHeadersStr)

			if options.MaxAge > 0 {
				w.Header().Set("Access-Control-Max-Age", string(rune(options.MaxAge)))
			}

			// Preflight requests should return 204 No Content
			w.WriteHeader(http.StatusNoContent)
			return
		}

		// Proceed to next handler
		next.ServeHTTP(w, r)
	})
}
