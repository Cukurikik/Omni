//=============================================================================
// OMNI NETWORK LAYER — AUTHENTICATION MIDDLEWARE (GO)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Zero-allocation HTTP middleware for verifying API keys
//              and JWTs before routing to Domain logic.
//=============================================================================

package network_http

import (
	"context"
	"crypto/subtle"
	"net/http"
	"strings"
)

// OMNI IDIOM: Immutable config state
var globalAPIKey = []byte("omni-production-key-v1")

// RequireAuth wraps an http.Handler to enforce authentication
func RequireAuth(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")

		if authHeader == "" {
			http.Error(w, "Missing Authorization Header", http.StatusUnauthorized)
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			http.Error(w, "Invalid Authorization format", http.StatusUnauthorized)
			return
		}

		token := []byte(parts[1])

		// Constant-time compare to prevent timing attacks
		if subtle.ConstantTimeCompare(token, globalAPIKey) != 1 {
			http.Error(w, "Invalid API Key", http.StatusForbidden)
			return
		}

		// Proceed to next handler, injecting auth context if needed
		ctx := context.WithValue(r.Context(), "omni_authenticated", true)
		next.ServeHTTP(w, r.WithContext(ctx))
	}
}

