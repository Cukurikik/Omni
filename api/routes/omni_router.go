package routes

import (
	"net/http"

	"omnitools/core"
	"omnitools/middleware"
	"omnitools/modules"
)

// RegisterOmniRoutes mengkonfigurasi rute dinamis /api/v1/omni/execute
// Menyambungkan 152 tools dalam backend secara terpusat!
func RegisterOmniRoutes(mux *http.ServeMux) {
	// Rantai Keamanan (Rate Limit -> Security Headers -> FinalShieldMiddleware -> Recovery)
	secureChain := func(next http.HandlerFunc) http.HandlerFunc {
		return core.Chain(next, core.RateLimitMiddleware, core.SecurityHeadersMiddleware, core.FinalShieldMiddleware, core.RecoveryMiddleware)
	}

	// OmniShield memeriksa payload untuk menghindari eksekutor memproses file "sampah" / korup / mismatch
	omniHandler := modules.OmniShield(OmniEngineHandler)

	// Wrap menjadi standar HTTP Handler, dan tambahkan Pipa Stream (FileQuarantineHandler) di atasnya!
	finalHandler := secureChain(middleware.FileQuarantineHandler(core.Wrap(omniHandler)))

	mux.HandleFunc("/api/v1/omni/execute", finalHandler)
	
	// API Khusus Pemeriksaan Pekerjaan
	mux.HandleFunc("/api/v1/omni/status", JobStatusHandler)
}

// OmniEngineHandler memproses payload setelah divalidasi oleh OmniShield
func OmniEngineHandler(c *core.OmniContext) {
	// Teruskan secara transparan ke UniversalToolHandler (Worker lama yang sudah solid)
	// Hanya saja, kini perlindungan OmniShield dan Core Middleware ada di atasnya!
	UniversalToolHandler(c.W, c.R)
}
