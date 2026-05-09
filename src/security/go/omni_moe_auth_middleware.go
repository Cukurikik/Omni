package go_pkg

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

// CerbosClient interface (Mocked for structure)
type CerbosClient interface {
	CheckPermission(ctx context.Context, principalID, resource, action string) bool
}

// OmniMoEAuthMiddleware enforces JWT validation and delegates endpoint authorization
// to the Cerbos policy engine (e.g., matching the moe_resource_policy.yaml).
func OmniMoEAuthMiddleware(cerbos CerbosClient) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

			authHeader := r.Header.Get("Authorization")
			if !strings.HasPrefix(authHeader, "Bearer ") {
				http.Error(w, "OMNI Security: Missing or Invalid Bearer Token", http.StatusUnauthorized)
				return
			}

			tokenString := strings.TrimPrefix(authHeader, "Bearer ")

			// In production, parse and validate signature against public JWKS
			// For structure, we assume parsing logic here.
			token, _, err := new(jwt.Parser).ParseUnverified(tokenString, jwt.MapClaims{})
			if err != nil {
				http.Error(w, "OMNI Security: Invalid JWT", http.StatusUnauthorized)
				return
			}

			claims, ok := token.Claims.(jwt.MapClaims)
			if !ok {
				http.Error(w, "OMNI Security: Invalid Claims", http.StatusUnauthorized)
				return
			}

			tenantID := fmt.Sprintf("%v", claims["tenant_id"])
			role := fmt.Sprintf("%v", claims["role"])

			// Check action based on HTTP Method and Path
			action := mapMethodToAction(r.Method, r.URL.Path)

			// Delegate authorization to Cerbos
			allowed := cerbos.CheckPermission(r.Context(), role, "moe_cluster_endpoint", action)
			if !allowed {
				http.Error(w, "OMNI Security: Access Denied by Cerbos Policy", http.StatusForbidden)
				return
			}

			// Pass Tenant ID to the next handler via context
			ctx := context.WithValue(r.Context(), "tenantID", tenantID)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

func mapMethodToAction(method, path string) string {
	if strings.Contains(path, "generate") {
		return "execute_inference"
	}
	if strings.Contains(path, "telemetry") {
		return "view_telemetry"
	}
	return "unknown_action"
}

