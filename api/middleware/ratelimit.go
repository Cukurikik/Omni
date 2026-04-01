package middleware

import (
	"encoding/json"
	"net/http"
	"strings"
	"sync"
	"time"

	"omnitools/services" // Menggunakan Kotak Hitam
)

// Konfigurasi Baju Zirah OMNI
const (
	MaxHeavyRequests = 5               // Maksimal 5 tugas berat
	WindowDuration   = 1 * time.Minute // Dalam rentang waktu 1 menit
)

// Struktur data pengunjung di RAM
type Visitor struct {
	Count    int
	LastSeen time.Time
}

var (
	visitors = make(map[string]*Visitor)
	mapMutex sync.Mutex
)

// Jalankan fungsi ini di main.go untuk membersihkan daftar IP lama agar RAM tidak bocor
func StartRateLimitCleaner() {
	for {
		time.Sleep(3 * time.Minute)
		mapMutex.Lock()
		for ip, v := range visitors {
			if time.Since(v.LastSeen) > 3*time.Minute {
				delete(visitors, ip)
			}
		}
		mapMutex.Unlock()
	}
}

// Ekstrak IP asli pengguna (mengabaikan proxy jika ada)
func getIP(r *http.Request) string {
	ip := r.Header.Get("X-Real-IP")
	if ip == "" {
		ip = r.Header.Get("X-Forwarded-For")
	}
	if ip == "" {
		ip = strings.Split(r.RemoteAddr, ":")[0]
	}
	return ip
}

// Fungsi Pelindung Utama (Middleware)
func HeavyTaskRateLimiter(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ip := getIP(r)

		mapMutex.Lock()
		v, exists := visitors[ip]

		if !exists {
			// Pengunjung baru
			visitors[ip] = &Visitor{Count: 1, LastSeen: time.Now()}
		} else {
			// Pengunjung lama, cek apakah sudah melewati 1 menit
			if time.Since(v.LastSeen) > WindowDuration {
				v.Count = 0 // Reset hitungan
			}

			v.Count++
			v.LastSeen = time.Now()

			// Jika melebihi batas!
			if v.Count > MaxHeavyRequests {
				mapMutex.Unlock()

				// 1. Catat ke Kotak Hitam OMNI!
				services.WriteLog("SECURITY", "RATE_LIMIT_EXCEEDED", "IP "+ip+" mencoba melakukan spam komputasi berat.")

				// 2. Tolak dengan JSON Universal Error
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusTooManyRequests) // Kode 429
				json.NewEncoder(w).Encode(map[string]interface{}{
					"success": false,
					"layer":   "SECURITY_GATEWAY",
					"code":    "ERR_SPAM_DETECTED",
					"message": "Anda melakukan terlalu banyak tugas berat. Harap tunggu 1 menit.",
				})
				return
			}
		}
		mapMutex.Unlock()

		// Lolos dari hadangan, silakan lanjut ke proses C++ atau Python
		next.ServeHTTP(w, r)
	}
}
