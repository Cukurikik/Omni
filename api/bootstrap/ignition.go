package bootstrap

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"omnitools/core"
	"omnitools/engine"
	"omnitools/middleware"
	"omnitools/services"
)

// ==========================================
// ⚡ OMNI-IGNITION: PRE-CONFIGURED GOD MODE
// ==========================================
// Package bootstrap adalah package tingkat tertinggi yang tidak diimpor
// oleh package lain manapun. Ia mengimpor SEMUA package OMNI
// (core, engine, middleware, services, routes) tanpa risiko import cycle.
//
// Developer hanya menulis di main.go:
//   bootstrap.Ignite(routes.SetupRoutes)
//
// Dan OMNI secara otomatis:
//   1. Membaca konfigurasi (appconfig.json)
//   2. Menyambung Firebase Firestore
//   3. Menyalakan Worker Pool (C++, Python, Golang)
//   4. Mengaktifkan Middleware (CORS, COOP/COEP, Logger)
//   5. Menghidupkan OMNI-SSR Render Engine
//   6. Menjalankan NEXUS Cluster (Master/Worker)
//   7. Recovery antrean WO (OMNI-AURA)
//   8. Graceful Shutdown (anti-zombie process)
//   9. Menampilkan War Banner
// ==========================================

// Ignite adalah "Percikan Ilahi" — satu fungsi untuk menyalakan seluruh alam semesta.
// Parameter registerRoutesFunc biasanya routes.SetupRoutes.
// Developer TIDAK PERLU memanggil apapun selain fungsi ini di main.go.
func Ignite(registerRoutesFunc func(*http.ServeMux)) {
	fmt.Println(core.T("IGNITION_START", nil))
	fmt.Println(core.T("CONVENTION_ACTIVE", nil))
	fmt.Println(core.T("GOD_MODE_ENGAGED", nil))

	// ==========================================
	// PHASE 1: AUTO-DISCOVERY KONFIGURASI
	// ==========================================
	log.Println(core.T("PHASE1_CONFIG", nil))
	services.InitLogger()
	core.LoadAppConfig(core.ResolveConfigPath("appconfig.json"))
	core.LoadConfig(core.ResolveConfigPath("omni_config.json"))
	core.LoadLingua() // Load dictionary immediately after appconfig
	loadEnvironmentVars()

	// ==========================================
	// PHASE 2: AUTO-CONNECT DATABASE (Firebase/WAL)
	// ==========================================
	log.Println(core.T("PHASE2_DB", nil))
	core.InitFirebase()
	core.InitDatabase()          // 🗄️ OMNI-DB: Database Agnostic Interface
	core.InitDevMode()           // 🔬 OMNI-DEV: Transparent Debugging Mode
	core.InitChameleon()         // 🎨 OMNI-CHAMELEON: CSS Framework Injection
	core.InitWasmRuntime()       // ⚡ OMNI-WASM: WebAssembly Sandbox Isolator
	core.InitIPC()               // 🔌 OMNI-UDS: Inter-Process Communication
	services.InitDBAutoHeal()    // 🗄️ OMNI-ORACLE: Database Schema Healer
	services.LoadCLIRegistry()   // Muat template alat CLI
	services.LoadClusterConfig() // Muat slave remote nodes (jika ada)
	middleware.InitSandbox()     // Pastikan folder karantina & cache siap

	// ==========================================
	// PHASE 3: AUTO-CONNECT EXECUTOR ENGINE
	// ==========================================
	log.Println(core.T("PHASE3_EXECUTOR", nil))
	core.GlobalExecutor = engine.ExecuteTool

	// ==========================================
	// PHASE 4: AUTO-START BACKGROUND GOROUTINES
	// ==========================================
	log.Println(core.T("PHASE4_BACKGROUND", nil))
	go core.StartBlackbox()                // ⬛ Janitor (Rotasi Log > 50MB)
	go services.StartCacheDestroyer()      // 🧹 Janitor (Pembersih Cache 1-Jam)
	go middleware.StartRateLimitCleaner()   // 🛡️ Anti-Spam Memory Cleaner
	go services.StartWorkerPool()          // 🏭 Pabrik Pekerja C++/Python (4 Workers, 100 Queue)
	go services.StartGoWorkerPool()        // 🏗️ Pabrik Pekerja Golang Internal (8 Workers, 200 Queue)
	go services.StartWALCompactor()        // 💾 Pembersih OMNI-AURA WAL otomatis

	// ==========================================
	// PHASE 5: OMNI-NEXUS DISTRIBUTED CLUSTER
	// ==========================================
	nexusRole := core.AppConfig.NexusCluster.Role
	if nexusRole == "master" {
		log.Println(core.T("PHASE5_MASTER", nil))
		core.StartFleetMonitor()
	} else if nexusRole == "worker" {
		myAddr := core.DetectMyAddress()
		log.Println(core.T("PHASE5_WORKER", map[string]string{"master_url": core.AppConfig.NexusCluster.MasterURL}))
		core.StartWorkerHeartbeat(myAddr)
	} else {
		log.Println(core.T("PHASE5_STANDALONE", nil))
	}

	// ==========================================
	// PHASE 6: OMNI-AURA RECOVERY PROTOCOL
	// ==========================================
	log.Println(core.T("PHASE6_AURA", nil))
	services.RecoverAndRequeueLostJobs()

	// ==========================================
	// PHASE 7: PRE-CONFIGURED ROUTER + SSR ENGINE
	// ==========================================
	log.Println(core.T("PHASE7_ROUTER", nil))
	mux := http.NewServeMux()

	// Daftarkan semua route (Convention: developer hanya panggil routes.SetupRoutes)
	registerRoutesFunc(mux)

	// OMNI-SSR Fallback Handler (Pre-configured)
	staticDir := "../release/public"
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// 🛡️ COOP/COEP Headers (SharedArrayBuffer + WASM support)
		w.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
		w.Header().Set("Cross-Origin-Embedder-Policy", "require-corp")
		w.Header().Set("Cross-Origin-Resource-Policy", "cross-origin")
		w.Header().Set("X-Powered-By", "OMNI-FRAMEWORK/1.3-SOVEREIGN")

		urlPath := r.URL.Path

		// 1. File statis (JS, CSS, gambar) → serve langsung
		if core.IsStaticAsset(urlPath) {
			filePath := filepath.Join(staticDir, urlPath)
			if _, err := os.Stat(filePath); err == nil {
				http.ServeFile(w, r, filePath)
				return
			}
		}

		// 2. Route SPA → OMNI-SSR Engine!
		ssrCtx := core.GetSSRContext(urlPath)
		ssrCtx.URL = r.URL.String()

		// Inject initial data (React hydration state)
		ssrCtx.InitialData = map[string]interface{}{
			"appName": core.AppConfig.AppName,
			"version": core.AppConfig.Version,
			"route":   urlPath,
			"ssr":     true,
		}

		core.ServeSSR(w, r, ssrCtx)
	})

	// ==========================================
	// PHASE 8: PRE-CONFIGURED MIDDLEWARE GALAXY
	// ==========================================
	log.Println(core.T("PHASE8_MIDDLEWARE", nil))

	// 🔬 OMNI-DEV: Profiling middleware (zero-cost di production)
	profiledMux := core.DevProfileMiddleware(mux)
	godHandler := ApplyGodMiddlewares(profiledMux)

	// ==========================================
	// PHASE 9: SERVER IGNITION + GRACEFUL SHUTDOWN
	// ==========================================
	serverAddr := core.GetServerAddr()

	srv := &http.Server{
		Addr:         serverAddr,
		Handler:      godHandler,
		ReadTimeout:  time.Duration(core.AppConfig.Server.ReadTimeoutSeconds) * time.Second,
		WriteTimeout: time.Duration(core.AppConfig.Server.WriteTimeoutSeconds) * time.Second,
	}

	// Start server in goroutine
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("💥 [FATAL] Ledakan Supernova: %v", err)
		}
	}()

	// WAR BANNER — Pamer kekuatan OMNI
	printWarBanner(serverAddr, nexusRole)

	// ==========================================
	// GRACEFUL SHUTDOWN (Pre-configured Anti-Crash)
	// ==========================================
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	fmt.Println(core.T("SHUTDOWN_SIGNAL", nil))
	services.WriteLog("SYSTEM", "INFO", "Shutdown process initiated...")

	ctxShutdown, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctxShutdown); err != nil {
		services.WriteLog("SYSTEM", "FATAL", fmt.Sprintf("Server mati paksa: %v", err))
		log.Fatal("💀 Server forced to shutdown:", err)
	}

	// Tutup koneksi Firebase Firestore
	core.CloseFirebase()

	// Tutup koneksi OMNI-DB (LocalWAL flush / Postgres disconnect)
	if core.DB != nil {
		core.DB.Close()
	}

	// Tutup OMNI-UDS IPC listener
	core.CloseIPC()

	fmt.Println(core.T("SHUTDOWN_SUCCESS", nil))
}

// ==========================================
// 🛡️ GOD MIDDLEWARES (CORS + Logger + COOP/COEP)
// ==========================================
func ApplyGodMiddlewares(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// PRE-CONFIGURED CORS — OMNI-VERB RESTful Matrix Compatible
		allowedOrigin := "*"
		if core.AppConfig != nil && len(core.AppConfig.Security.CorsAllowedOrigins) > 0 {
			allowedOrigin = core.AppConfig.Security.CorsAllowedOrigins[0]
		}
		w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, X-OMNI-KEY, X-NEXUS-COMMANDER")
		w.Header().Set("Access-Control-Max-Age", "86400") // Cache preflight selama 24 jam

		// 🛡️ OMNI-VERB: Cegat OPTIONS sebelum masuk ke route (CORS Preflight)
		// Browser hanya mengecek izin → balas 200 OK → BERHENTI.
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		// Pre-configured Blackbox Logger
		log.Printf("📡 [INCOMING] %s %s from %s", r.Method, r.URL.Path, r.RemoteAddr)

		next.ServeHTTP(w, r)
	})
}

// loadEnvironmentVars membaca variabel lingkungan penting
func loadEnvironmentVars() {
	apiSecret := os.Getenv("OMNI_AI_SECRET_KEY")
	if apiSecret == "" {
		services.WriteLog("SYSTEM", "WARN_ENV", "OMNI_AI_SECRET_KEY tidak ditemukan di environment!")
	}
}

// printWarBanner menampilkan war banner OMNI saat server menyala — V1.3 SOVEREIGN EDITION
func printWarBanner(serverAddr string, nexusRole string) {
	fmt.Println("\n╔══════════════════════════════════════════════════════════════╗")
	fmt.Println("║                                                              ║")
	fmt.Printf("║   🔥 %s v%s — KEDAULATAN MUTLAK\n", core.AppConfig.AppName, core.AppConfig.Version)
	fmt.Println("║   ⚔️  BARE-METAL SOVEREIGNTY FRAMEWORK                       ║")
	fmt.Println("║                                                              ║")
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Println("║  📋 INFRASTRUKTUR INTI                                      ║")
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Printf("  🌍 Environment            : %s\n", core.AppConfig.Environment)
	fmt.Printf("  📦 Max Upload             : %dGB\n", core.AppConfig.Storage.MaxUploadGB)
	fmt.Printf("  🏭 Worker Pool C++/Python : %d Pekerja\n", core.AppConfig.Engine.MaxConcurrentWorkers)
	fmt.Printf("  🏗️ Worker Pool Golang     : %d Pekerja\n", core.AppConfig.Engine.GoWorkers)
	fmt.Printf("  ⚙️  FFmpeg Threads         : %d\n", core.AppConfig.Engine.FFmpegThrottleThreads)
	fmt.Println("  🧹 Janitor Ephemeral      : Aktif")
	fmt.Printf("  🛡️ Rate Limiter           : %d req/s per IP\n", core.AppConfig.Security.RateLimitPerSecond)
	fmt.Println("  🌐 SSR Engine             : Aktif (OMNI-RENDER)")

	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Println("║  🏛️  PILAR KEDAULATAN V1.3                                   ║")
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")

	// 🗄️ OMNI-DB
	dbEngine := "local"
	if core.AppConfig.Database.Engine != "" {
		dbEngine = core.AppConfig.Database.Engine
	}
	fmt.Printf("  🗄️ OMNI-DB                : %s\n", strings.ToUpper(dbEngine))

	// 🔌 OMNI-ADAPTER
	adapterCount := core.GetAdapterCount()
	if adapterCount > 0 {
		fmt.Printf("  🔌 OMNI-ADAPTER           : %d adapter(s)\n", adapterCount)
	} else {
		fmt.Println("  🔌 OMNI-ADAPTER           : 0 adapter")
	}

	// 🔬 OMNI-DEV
	if core.DevMode {
		fmt.Println("  🔬 OMNI-DEV               : AKTIF")
	} else {
		fmt.Println("  🔬 OMNI-DEV               : OFF")
	}

	// 📡 OMNI-STREAM
	fmt.Println("  📡 OMNI-STREAM            : SSE Aktif")

	// 🌌 OMNI-TITAN
	fmt.Printf("  🌌 OMNI-TITAN             : %dGB Buffer × %d Slots (%dGB RAM Pool)\n",
		core.GetTitanCapacityBytes()/(1024*1024*1024),
		core.TitanMaxSlots,
		core.GetTitanMaxPoolBytes()/(1024*1024*1024))

	// 🔐 OMNI-LOCK
	fmt.Printf("  🔐 OMNI-LOCK              : %s\n", core.LockFileStatus())

	// 🧪 OMNI-TEST
	fmt.Println("  🧪 OMNI-TEST              : /api/v1/test/deep")

	// 📈 PROMETHEUS
	fmt.Println("  📈 PROMETHEUS             : 21+ Metrics (/api/v1/omni/metrics)")

	// 🎨 OMNI-CHAMELEON
	fmt.Printf("  🎨 OMNI-CHAMELEON         : %s\n", core.GetChameleonStatus())

	// ⚡ OMNI-WASM
	fmt.Printf("  ⚡ OMNI-WASM              : %s\n", core.GetWasmStatus())

	// 🔌 OMNI-UDS
	fmt.Printf("  🔌 OMNI-UDS (IPC)         : %s\n", core.GetIPCStatus())

	// 👑 NEXUS
	nexusRoleBanner := strings.ToUpper(nexusRole)
	if nexusRoleBanner == "MASTER" {
		fmt.Println("  👑 NEXUS Cluster          : MASTER (Jenderal Armada)")
	} else if nexusRoleBanner == "WORKER" {
		fmt.Printf("  🪖 NEXUS Cluster          : WORKER → %s\n", core.AppConfig.NexusCluster.MasterURL)
	} else {
		fmt.Println("  ⚪ NEXUS Cluster          : STANDALONE")
	}

	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Printf("  🚀 OMNI GATEWAY           : http://%s\n", serverAddr)
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Println("  ⚡ Convention Over Configuration   : ACTIVE")
	fmt.Println("  🔥 Pre-Configured God Mode        : ON")
	fmt.Println("  🗄️ Vendor Lock-in                 : DESTROYED")
	fmt.Println("  📡 Battery-Efficient               : SSE ACTIVE")
	fmt.Println("  🏛️  Kedaulatan Mutlak              : V1.3 SOVEREIGN")
	fmt.Println("╚══════════════════════════════════════════════════════════════╝")
}
