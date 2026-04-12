package middleware

import (
	"log"
	"net/http"
	"os"

	"omnitools/cloud_apis"
)

// APIKeyAuthGuard adalah Bouncer yang menjaga pintu masuk ke semua Endpoint OMNI.
// Ia hanya akan mengizinkan orang yang memiliki Kunci Rahasia OMNI yang benar.
func APIKeyAuthGuard(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Dapatkan Kunci dari brankas .env
		secretKey := os.Getenv("OMNI_AI_SECRET_KEY")
		// Jika kunci belum diset di server, izinkan lewat (Mode Terbuka / Development Keras)
		if secretKey == "" {
			next.ServeHTTP(w, r)
			return
		}

		// Periksa header, apakah klien membawa kunci?
		clientKey := r.Header.Get("X-OMNI-API-KEY")
		if clientKey == "" {
			// Coba periksa Bearer Token (sebagai alternatif jika memakai UI standard)
			authHeader := r.Header.Get("Authorization")
			if len(authHeader) > 7 && authHeader[:7] == "Bearer " {
				clientKey = authHeader[7:]
			}
		}

		if clientKey == secretKey {
			// Superadmin API Key match! Bypass JWT
			next.ServeHTTP(w, r)
			return
		}

		// Mode JWT (Model A: Enterprise Legacy Bridge)
		if len(clientKey) > 20 { 
			// Panjang lebih dari 20 berarti kemungkinan JWT.
			authBridge := cloud_apis.NewFirebaseAuthBridge(os.Getenv("FIREBASE_PROJECT"), "")
			_, err := authBridge.VerifyIDToken(r.Context(), clientKey)
			
			if err == nil {
				// JWT Sah, izinkan lewat
				next.ServeHTTP(w, r)
				return
			}
			log.Printf("[SECURITY] JWT Validation Failed: %v", err)
		}

		log.Printf("[SECURITY] WARN_UNAUTHORIZED: Ada penyusup mencoba mengakses endpoint dengan Kunci/JWT Palsu!")
		http.Error(w, `{"success": false, "message": "Akses Ditolak: Kredensial Enterprise/JWT tidak valid."}`, http.StatusUnauthorized)
		return
	}
}
