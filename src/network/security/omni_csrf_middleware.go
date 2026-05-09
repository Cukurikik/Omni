package security

// omni_csrf_middleware.go — CSRF Token Verification
// Layer: Network / Go
//
// HTTP middleware that implements the Double Submit Cookie pattern
// to prevent Cross-Site Request Forgery attacks. Zero mock.

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"net/http"
)

const (
	CSRFCookieName = "OMNI_CSRF_TOKEN"
	CSRFHeaderName = "X-CSRF-Token"
)

// generateToken creates a cryptographically secure 32-byte CSRF token.
func generateToken() (string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.StdEncoding.EncodeToString(b), nil
}

// OmniCSRFMiddleware wraps an http.Handler with CSRF protection.
func OmniCSRFMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		// Safe methods do not require CSRF validation, but we should ensure the cookie exists
		if r.Method == http.MethodGet || r.Method == http.MethodHead || r.Method == http.MethodOptions {
			cookie, err := r.Cookie(CSRFCookieName)
			if err != nil || cookie.Value == "" {
				// Generate and set a new token
				token, genErr := generateToken()
				if genErr == nil {
					http.SetCookie(w, &http.Cookie{
						Name:     CSRFCookieName,
						Value:    token,
						Path:     "/",
						HttpOnly: false, // Must be readable by frontend JS to set the header
						Secure:   true,  // HTTPS only
						SameSite: http.SameSiteStrictMode,
					})
				}
			}
			next.ServeHTTP(w, r)
			return
		}

		// Unsafe methods (POST, PUT, DELETE) require validation
		cookie, err := r.Cookie(CSRFCookieName)
		if err != nil || cookie.Value == "" {
			http.Error(w, "Forbidden - CSRF Cookie Missing", http.StatusForbidden)
			return
		}

		headerToken := r.Header.Get(CSRFHeaderName)
		if headerToken == "" {
			http.Error(w, "Forbidden - CSRF Header Missing", http.StatusForbidden)
			return
		}

		// Constant-time string comparison to prevent timing attacks
		if subtle.ConstantTimeCompare([]byte(cookie.Value), []byte(headerToken)) != 1 {
			http.Error(w, "Forbidden - CSRF Token Mismatch", http.StatusForbidden)
			return
		}

		next.ServeHTTP(w, r)
	})
}
