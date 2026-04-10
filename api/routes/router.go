package routes

import (
	"net/http"
	"time"

	"omnitools/core"
	"omnitools/engine"
	"omnitools/middleware"
	"omnitools/services"
)

// SetupRoutes merakit seluruh jalur API dan UI menggunakan Omni-HTTP Framework
func SetupRoutes(mux *http.ServeMux) {
	// ==========================================
	// 1. OMNI-HTTP FRAMEWORK (BARU)
	// ==========================================
	// Route Publik tanpa Session Auth
	mux.HandleFunc("/api/v1/login", core.LoggerMiddleware(core.Wrap(LoginHandler)))

	// Contoh rute menggunakan perlindungan OmniContext penuh
	mux.HandleFunc("/api/v1/execute/test", core.LoggerMiddleware(core.AuthMiddleware(core.Wrap(executeTestHandler))))

	// Rute Inti OMNI Framework (Mempersatukan 152 Tools)
	RegisterOmniRoutes(mux)

	// 🛣️ OMNI-ROUTER: File-Based Auto API Routes
	// Dihasilkan otomatis oleh CLI (omni dev / omni build)
	RegisterAutoRoutes(mux)

	// ==========================================
	// 2. RUTE SYSTEM & ASSET CACHE
	// ==========================================
	mux.Handle("/hls/", middleware.CORSStreamHandler(http.StripPrefix("/hls/", http.FileServer(http.Dir(middleware.CacheDir)))))
	mux.Handle("/download/", http.StripPrefix("/download/", http.FileServer(http.Dir("../release/omni_cache/"))))

	// ==========================================
	// 3. OMNI TOOLS (LEGACY / WORKER MODE)
	// Mempertahankan auth API Key untuk bot rekayasa komputasi
	// ==========================================
	mux.HandleFunc("/api/v1/tools/universal/",
		middleware.APIKeyAuthGuard(middleware.HeavyTaskRateLimiter(
			middleware.FileQuarantineHandler(UniversalToolHandler),
		)),
	)
	mux.HandleFunc("/api/v1/tools/audio/detect-drop",
		middleware.APIKeyAuthGuard(middleware.HeavyTaskRateLimiter(
			middleware.FileQuarantineHandler(AudioDropHandler),
		)),
	)
	mux.HandleFunc("/api/v1/tools/pdf/",
		middleware.APIKeyAuthGuard(middleware.HeavyTaskRateLimiter(
			middleware.FileQuarantineHandler(PdfToolHandler),
		)),
	)
	mux.HandleFunc("/api/v1/tools/converter/",
		middleware.APIKeyAuthGuard(middleware.HeavyTaskRateLimiter(
			middleware.FileQuarantineHandler(ConverterToolHandler),
		)),
	)

	// ==========================================
	// 4. WEBSOCKET & TUS
	// ==========================================
	mux.HandleFunc("/ws/ai-chat", middleware.HeavyTaskRateLimiter(AiChatStreamHandler))
	mux.HandleFunc("/ws/swarm", middleware.HeavyTaskRateLimiter(WebRTCSwarmHandler))
	mux.HandleFunc("/api/v1/monitor/stream", services.MonitorHandler)
	mux.HandleFunc("/api/v1/omni/metrics", MetricsHandler)

	// 📡 OMNI-RESONANCE: Live-Reload WebSocket
	mux.HandleFunc("/ws/omni_live", core.ResonanceHandler)
	mux.HandleFunc("/api/internal/trigger-reload", core.TriggerReloadHandler)

	// 🌐 OMNI-NEXUS: Distributed Cluster API
	if core.AppConfig.NexusCluster.Role == "master" {
		mux.HandleFunc("/api/nexus/heartbeat", core.NexusHeartbeatHandler)
		mux.HandleFunc("/api/nexus/status", core.NexusStatusHandler)
	}

	// 📡 OMNI-BROADCASTER: Job Progress Real-Time WebSocket (Legacy)
	mux.HandleFunc("/ws/jobs", core.JobStreamHandler)

	// 📡 OMNI-STREAM: SSE — Battery-Efficient Job Monitoring (Modern)
	mux.HandleFunc("/api/v1/stream/jobs", core.SSEJobStreamHandler)

	// 🔌 OMNI-ADAPTER: Third-Party Integration Status
	mux.HandleFunc("/api/v1/adapters/status", AdapterStatusHandler)

	// 🔬 OMNI-DEV: System Inspection (hanya aktif saat development)
	mux.HandleFunc("/api/v1/dev/inspect", core.DevInspectHandler)

	// 🧪 OMNI-TEST: Deep Validation Engine (V1.3)
	mux.HandleFunc("/api/v1/test/deep", core.DeepTestHandler)

	// ⚡ OMNI-WASM: WebAssembly Module Status (V1.3)
	mux.HandleFunc("/api/v1/wasm/status", WasmStatusHandler)

	mux.HandleFunc("/api/v1/tus", middleware.APIKeyAuthGuard(TusHandler))
	mux.HandleFunc("/api/v1/tus/", middleware.APIKeyAuthGuard(TusHandler))

	// ==========================================
	// 5. THE ALCHEMIST
	// ==========================================
	mux.HandleFunc("/api/v1/system/hotswap", middleware.APIKeyAuthGuard(HotSwapHandler))

	// ==========================================
	// 6. GHOST HANDLERS INJECTION
	// ==========================================
	for path, handler := range OracleMockRoutes {
		mux.HandleFunc(path, handler)
	}

	// ==========================================
	// 7. ⚛️ ENGINE CORE: ASYNC PROCESSING (Zero-RAM)
	// ==========================================
	// Upload file → Job ID instant → Polling status → Download hasil
	mux.HandleFunc("/api/v1/process", middleware.APIKeyAuthGuard(engine.AsyncProcessHandler))
	mux.HandleFunc("/api/v1/job", engine.JobStatusHandler)
	mux.HandleFunc("/api/v1/download/result", engine.DownloadHandler)

	// Nyalakan pembersihan job lama (setiap 1 jam, hapus yg > 24 jam)
	engine.Tracker.StartCleanupWorker(1*time.Hour, 24*time.Hour)
}

// ==========================================
// TEST HANDLERS UNTUK OMNICONTEXT
// ==========================================

// LoginHandler memberikan sesi token dummy menggunakan sistem bare-metal baru
func LoginHandler(c *core.OmniContext) {
	// TODO: Validasi password dari body dengan c.ParseBody(..)

	token := core.GenerateSession("user_123", "ADMIN")

	// Set Cookie super aman (Hanya bisa dibaca oleh Backend)
	http.SetCookie(c.W, &http.Cookie{
		Name:     "omni_session",
		Value:    token,
		HttpOnly: true, // Tidak bisa dicuri oleh XSS (JavaScript UI)
		Path:     "/",
	})

	c.JSON(200, true, "Login Sukses via Omni-HTTP Engine", nil)
}

// executeTestHandler adalah payload execution dgn Context baru
func executeTestHandler(c *core.OmniContext) {
	toolID := c.GetParam("tool_id", "unknown")

	if toolID == "unknown" {
		c.JSON(400, false, "Tool ID tidak boleh kosong!", nil)
		return
	}

	c.JSON(200, true, "Proses sukses melewati Firewall OmniContext", map[string]string{
		"download_url": "/api/v1/download/omni_" + toolID + ".mp4",
	})
}
