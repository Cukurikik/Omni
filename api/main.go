package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"runtime"
	"sync/atomic"
	"syscall"
	"time"

	"omnitools/middleware"
	"omnitools/telepathy"
)

// ==========================================
// 🌐 OMNI TELEPATHY GATEWAY — Production v2.0
// ==========================================
// Full middleware stack: CORS → RateLimit → Auth → Handler
// Graceful shutdown, metrics, readiness probes.

var (
	requestCount  uint64
	startTime     time.Time
	gatewayReady  int32
)

func invokeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"status": "Err", "error": "Hanya method POST yang diizinkan pada OMNI Gateway"}`, http.StatusMethodNotAllowed)
		return
	}

	atomic.AddUint64(&requestCount, 1)

	var req telepathy.OmniRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"status": "Err", "error": "Format instruksi Omni telepati tidak valid"}`, http.StatusBadRequest)
		return
	}

	// Dispatch to the core nervous system
	res := telepathy.TelepathyRouter(r.Context(), req)

	// Send back monadic response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	uptime := time.Since(startTime).Round(time.Second)
	fmt.Fprintf(w, `{"status":"Ok","message":"OMNI-NEXUS-ULTRA Kernel Active","uptime":"%s","time":"%s"}`,
		uptime, time.Now().UTC().Format(time.RFC3339))
}

func readinessHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if atomic.LoadInt32(&gatewayReady) == 1 {
		fmt.Fprint(w, `{"status":"Ok","ready":true}`)
	} else {
		w.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprint(w, `{"status":"Err","ready":false}`)
	}
}

func metricsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	uptime := time.Since(startTime).Seconds()
	totalReqs := atomic.LoadUint64(&requestCount)

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	json.NewEncoder(w).Encode(map[string]interface{}{
		"uptime_seconds":     uptime,
		"total_requests":     totalReqs,
		"goroutines":         runtime.NumGoroutine(),
		"heap_alloc_mb":      float64(memStats.HeapAlloc) / 1024 / 1024,
		"sys_memory_mb":      float64(memStats.Sys) / 1024 / 1024,
		"gc_cycles":          memStats.NumGC,
		"telepathy_routes":   95,
		"cloud_api_wrappers": 58,
		"ai_models":          20,
		"service_orchestrators": 4,
	})
}

func main() {
	startTime = time.Now()

	mux := http.NewServeMux()

	// ── PROBES (No auth required) ─────────────────────────────────
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/readiness", readinessHandler)
	mux.HandleFunc("/metrics", metricsHandler)

	// ── TELEPATHY CORE (Auth + RateLimit protected) ───────────────
	protectedInvoke := middleware.HeavyTaskRateLimiter(
		middleware.APIKeyAuthGuard(invokeHandler),
	)
	mux.HandleFunc("/invoke", protectedInvoke)
	mux.HandleFunc("/api/v1/invoke", protectedInvoke)

	// ── MIDDLEWARE STACK: CORS → Handler ──────────────────────────
	handler := middleware.CORSStreamHandler(mux)

	server := &http.Server{
		Addr:         ":8080",
		Handler:      handler,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 60 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// ── BACKGROUND SERVICES ──────────────────────────────────────
	go middleware.StartRateLimitCleaner()

	// ── GRACEFUL SHUTDOWN ────────────────────────────────────────
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		// Mark gateway as ready
		atomic.StoreInt32(&gatewayReady, 1)

		log.Println("=========================================================")
		log.Println("  🌐 ANTIGRAVITY OMNI TELEPATHY GATEWAY v2.0")
		log.Println("=========================================================")
		log.Println("  🛡️  Middleware    : CORS → RateLimit → APIKeyAuth")
		log.Println("  🟢 Listening     : http://0.0.0.0:8080")
		log.Println("  📡 Endpoints     : /invoke, /api/v1/invoke")
		log.Println("  ❤️  Probes        : /health, /readiness, /metrics")
		log.Printf("  🧠 Telepathy     : 95+ routes across 9 sub-routers")
		log.Printf("  ☁️  Cloud APIs    : 58 GCP wrappers operational")
		log.Printf("  🤖 AI Models     : 20 models (5 tiers)")
		log.Printf("  🔧 Orchestrators : 4 (PaaS + Observability + CICD + Data)")
		log.Println("=========================================================")

		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Fatal OMNI Gateway Error: %v\n", err)
		}
	}()

	// Wait for shutdown signal
	sig := <-quit
	log.Printf("🛑 Shutdown signal received: %v", sig)
	log.Println("🛑 Gracefully shutting down OMNI Gateway...")

	// Mark as not ready for K8s
	atomic.StoreInt32(&gatewayReady, 0)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("OMNI Gateway forced shutdown: %v\n", err)
	}

	log.Println("✅ OMNI Gateway shutdown complete. Sampai jumpa, Astronaut.")
}