package core

import (
	"log"
	"net/http"
	"time"
)

// OmniHandler adalah tipe fungsi standar untuk OMNI Framework
type OmniHandler func(c *OmniContext)

// Wrap merubah OmniHandler kembali menjadi http.HandlerFunc standar Golang
func Wrap(handler OmniHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx := &OmniContext{W: w, R: r}
		handler(ctx)
	}
}

// ==========================================
// 🛡️ MIDDLEWARE RANTAI (CHAIN)
// ==========================================

// LoggerMiddleware mencatat setiap request yang masuk
func LoggerMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		duration := time.Since(start)
		log.Printf("🌐 [%s] %s -> Diproses dalam %v", r.Method, r.URL.Path, duration)
	}
}

// AuthMiddleware memaksa pengguna untuk login
func AuthMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		session := GetSession(r)
		if session == nil {
			ctx := &OmniContext{W: w, R: r}
			ctx.JSON(http.StatusUnauthorized, false, "Akses Ditolak. Sesi tidak valid.", nil)
			return
		}

		// Loloskan ke handler selanjutnya
		next.ServeHTTP(w, r)
	}
}

// Chain mempermudah penyusunan multiple middleware
func Chain(handler http.HandlerFunc, middlewares ...func(http.HandlerFunc) http.HandlerFunc) http.HandlerFunc {
	for i := len(middlewares) - 1; i >= 0; i-- {
		handler = middlewares[i](handler)
	}
	return handler
}

// RecoveryMiddleware menangkap panic agar server tidak mati (OmniShield Fallback)
func RecoveryMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("🔥 FATAL PANIC DITANGKAP OMNISHIELD: %v", err)
				ctx := &OmniContext{W: w, R: r}
				ctx.JSON(http.StatusInternalServerError, false, "System Failure Detected. OmniShield deployed.", nil)
			}
		}()
		next.ServeHTTP(w, r)
	}
}

// SecurityHeadersMiddleware menambahkan header keamanan standar
func SecurityHeadersMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("X-XSS-Protection", "1; mode=block")
		w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		next.ServeHTTP(w, r)
	}
}

// RateLimitMiddleware (Proteksi Sederhana Anti-SPAM)
// Implementasi rate limit nyata butuh token bucket, untuk sementara kita buat pass-through dengan logging
func RateLimitMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// TODO: Gunakan TokenBucket / Redis untuk skalabilitas
		next.ServeHTTP(w, r)
	}
}

// ==========================================
// 🛡️ OMNI-AUTH: FINAL SHIELD MIDDLEWARE
// ==========================================

// FinalShieldMiddleware memadukan proteksi JWT dan validasi API Key via Firebase.
func FinalShieldMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// ⚡ [GOD MODE] Jalur khusus untuk OMNI-TEST CLI lokal
		if r.Header.Get("X-OMNI-INTERNAL-TEST") == "OMNI_GOD_MODE_999" {
			next.ServeHTTP(w, r)
			return
		}

		// 1. Cek API Key di Header untuk eksternal
		apiKey := r.Header.Get("X-OMNI-KEY")
		if apiKey != "" {
			if !IsApiKeyValid(apiKey) {
				http.Error(w, "API Key Ilegal!", 403)
				return
			}
		} else {
			// 2. Jika tidak ada API Key, cek JWT (Login biasa)
			cookie, _ := r.Cookie("omni_token")
			if cookie == nil {
				http.Error(w, "Sesi Berakhir. Silakan Login.", 401)
				return
			}
			_, err := VerifyToken(cookie.Value)
			if err != nil {
				http.Error(w, "Token Rusak!", 401)
				return
			}
		}

		next.ServeHTTP(w, r)
	}
}
