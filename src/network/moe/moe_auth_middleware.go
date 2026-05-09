// moe_auth_middleware.go — Network / API Gateway
// Layer: Network / Security — MoE Access Control
//
// Middleware for the MoE HTTP Gateway. Validates JWTs, extracts tenant IDs,
// and ensures the caller has valid access rights to the requested model.

package network_moe

import (
	"context"
	"errors"
	"net/http"
	"strings"
)

// ContextKey used to store authenticated tenant info in the request context.
type ContextKey string

const TenantContextKey ContextKey = "tenant_id"

var (
	ErrMissingAuthHeader  = errors.New("missing authorization header")
	ErrInvalidTokenFormat = errors.New("invalid token format")
	ErrInvalidSignature   = errors.New("invalid token signature")
)

// Mock JWT Validator
type JWTValidator interface {
	ValidateToken(token string) (tenantID string, err error)
}

// Dummy implementation for Zero-Mock standalone build
type StandardJWTValidator struct {
	secret string
}

func NewStandardJWTValidator(secret string) *StandardJWTValidator {
	return &StandardJWTValidator{secret: secret}
}

func (v *StandardJWTValidator) ValidateToken(token string) (string, error) {
	// In production, use golang-jwt/jwt.
	// For this module, we simulate validation:
	if token == "" || token == "invalid" {
		return "", ErrInvalidSignature
	}
	// Extract tenant ID (mock: assume token string is the tenant ID)
	return token, nil
}

// MoEAuthMiddleware wraps an http.Handler with JWT validation.
func MoEAuthMiddleware(validator JWTValidator) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, ErrMissingAuthHeader.Error(), http.StatusUnauthorized)
				return
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
				http.Error(w, ErrInvalidTokenFormat.Error(), http.StatusUnauthorized)
				return
			}

			tokenString := parts[1]

			tenantID, err := validator.ValidateToken(tokenString)
			if err != nil {
				http.Error(w, err.Error(), http.StatusUnauthorized)
				return
			}

			// Add TenantID to context
			ctx := context.WithValue(r.Context(), TenantContextKey, tenantID)

			// Call the next handler
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// GetTenantID extracts the tenant ID from the context.
func GetTenantID(ctx context.Context) (string, bool) {
	tenantID, ok := ctx.Value(TenantContextKey).(string)
	return tenantID, ok
}

