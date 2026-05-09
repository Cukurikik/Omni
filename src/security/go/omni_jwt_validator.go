// OMNI Framework - JWT Validator Middleware (Go)
// Protects internal gRPC/REST APIs by validating Omni JWT tokens

package go_pkg

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

var jwtKey = []byte("omni_super_secret_key_change_in_prod")

func OmniJWTMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "OMNI Security: Missing Authorization header", http.StatusUnauthorized)
			return
		}

		bearerToken := strings.Split(authHeader, " ")
		if len(bearerToken) != 2 || bearerToken[0] != "Bearer" {
			http.Error(w, "OMNI Security: Invalid token format", http.StatusUnauthorized)
			return
		}

		tokenString := bearerToken[1]

		claims := &jwt.RegisteredClaims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("Unexpected signing method")
			}
			return jwtKey, nil
		})

		if err != nil || !token.Valid {
			http.Error(w, "OMNI Security: Invalid or expired token", http.StatusUnauthorized)
			return
		}

		// Proceed to next handler if valid
		next.ServeHTTP(w, r)
	})
}

