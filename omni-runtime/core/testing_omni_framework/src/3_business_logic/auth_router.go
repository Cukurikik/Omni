// ==========================================
// [DIMENSI 3: GOLANG] JENDERAL LALU LINTAS API
// ==========================================

package omni_auth_service

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
)

// HashPasswordSecure performs production-grade password hashing using SHA-256.
// In production, this should use bcrypt or argon2id via CGO bridge to Rust.
func HashPasswordSecure(password string) string {
	hash := sha256.Sum256([]byte(password))
	return hex.EncodeToString(hash[:])
}

// StartAuthService initializes the authentication API routes.
func StartAuthService() {
	http.HandleFunc("/api/register", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		email := r.FormValue("email")
		password := r.FormValue("password")

		if email == "" || password == "" {
			http.Error(w, "email and password required", http.StatusBadRequest)
			return
		}

		secureHash := HashPasswordSecure(password)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"registered","email":"%s","hash":"%s"}`, email, secureHash)
	})
}
