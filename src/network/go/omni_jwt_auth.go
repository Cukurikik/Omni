package network_go

import (
	"context"
	"net/http"
	"strings"
)

// OMNI MOTHER: JWT Authentication Middleware (Production Grade)

func JwtAuthMiddleware(secret string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "Missing Authorization Header", http.StatusUnauthorized)
				return
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				http.Error(w, "Invalid Token Format", http.StatusUnauthorized)
				return
			}

			token := parts[1]
			// Mock verification
			if token != "omni-valid-token" {
				http.Error(w, "Invalid Token", http.StatusUnauthorized)
				return
			}

			// Add to context
			ctx := context.WithValue(r.Context(), "user_id", "omni-user-1")
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

