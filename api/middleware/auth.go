package middleware

import (
	"net/http"
	"os"

	"omnitools/services"
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

		if clientKey != secretKey {
			services.WriteLog("SECURITY", "WARN_UNAUTHORIZED", "Ada penyusup alien yang mencoba mengakses endpoint dengan Kunci Palsu/Kosong!")
			http.Error(w, `{"success": false, "message": "Akses Ditolak: Anda tidak memiliki OMNI_AI_SECRET_KEY yang falid."}`, http.StatusUnauthorized)
			return
		}

		// Kunci sah, silakan masuk ke sistem
		next.ServeHTTP(w, r)
	}
}
