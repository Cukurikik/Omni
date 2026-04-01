package main

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
	"omnitools/routes"
	"omnitools/services"
)

// ==========================================
// GERBANG LINTAS DOMAIN (CORS Middleware)
// ==========================================
func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Baca CORS origins dari AppConfig (jika sudah dimuat)
		allowedOrigin := "*"
		if core.AppConfig != nil && len(core.AppConfig.Security.CorsAllowedOrigins) > 0 {
			allowedOrigin = core.AppConfig.Security.CorsAllowedOrigins[0]
		}
		w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
		w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

// ==========================================
// PEMBACA BRANKAS RAHASIA (.env Loader)
// ==========================================
func loadEnvironment() {
	apiSecret := os.Getenv("OMNI_AI_SECRET_KEY")
	if apiSecret == "" {
		services.WriteLog("SYSTEM", "WARN_ENV", "OMNI_AI_SECRET_KEY tidak ditemukan di environment!")
	}
}

// ==========================================
// FUNGSI UTAMA (ENTRY POINT)
// ==========================================
func main() {
	fmt.Println("🚀 Menyalakan OMNI TOOLS API Gateway...")

	// ==========================================
	// 🔌 OMNI-SYNC: SUNTIKAN EKSEKUTOR GENERATED
	// ==========================================
	// Menghubungkan Router hasil Metaprogramming CLI ke Orisinal Orchestrator
	core.GlobalExecutor = engine.ExecuteTool

	// ==========================================
	// 📖 THE OMNI READER: Muat Konfigurasi Pusat
	// ==========================================
	services.InitLogger()
	core.LoadAppConfig(core.ResolveConfigPath("appconfig.json"))
	core.InitFirebase() // 🔥 OMNI-DB: Firebase Firestore
	core.LoadConfig(core.ResolveConfigPath("omni_config.json"))
	loadEnvironment()
	services.InitDBAutoHeal()    // 🗄️ OMNI-ORACLE: Database Schema Healer
	services.LoadCLIRegistry()   // Muat template alat CLI
	services.LoadClusterConfig() // Muat slave remote nodes (jika ada)
	middleware.InitSandbox()     // Pastikan folder karantina & cache siap

	// ==========================================
	// NYALAKAN MESIN LATAR BELAKANG (Background Goroutines)
	// ==========================================
	go core.StartBlackbox()               // ⬛ Janitor (Rotasi Log > 50MB)
	go services.StartCacheDestroyer()     // 🧹 Janitor (Pembersih Cache 1-Jam)
	go middleware.StartRateLimitCleaner() // 🛡️ Anti-Spam Memory Cleaner
	go services.StartWorkerPool()         // 🏭 Pabrik Pekerja C++/Python (4 Workers, 100 Queue)
	go services.StartGoWorkerPool()       // 🏗️ Pabrik Pekerja Golang Internal (8 Workers, 200 Queue)
	go services.StartWALCompactor()       // 💾 Pembersih OMNI-AURA WAL otomatis

	// ==========================================
	// 🌐 OMNI-NEXUS: DISTRIBUTED CLUSTER ENGINE
	// ==========================================
	nexusRole := core.AppConfig.NexusCluster.Role
	if nexusRole == "master" {
		log.Println("👑 [OMNI-NEXUS] Inisialisasi sebagai MASTER NODE — Fleet Monitor Aktif")
		core.StartFleetMonitor()
	} else if nexusRole == "worker" {
		myAddr := core.DetectMyAddress()
		log.Printf("🪖 [OMNI-NEXUS] Inisialisasi sebagai WORKER NODE — Heartbeat ke %s", core.AppConfig.NexusCluster.MasterURL)
		core.StartWorkerHeartbeat(myAddr)
	}

	// ==========================================
	// 🧟 PROTOKOL KEBANGKITAN OMNI-AURA
	// ==========================================
	// Panggil setelah antrean (Worker Pool) siap
	services.RecoverAndRequeueLostJobs()

	// ==========================================
	// SETUP ROUTER
	// ==========================================
	mux := http.NewServeMux()

	// 🌊 DELEGASI RUTE KE OMNI-HTTP FRAMEWORK
	routes.SetupRoutes(mux)

	// --- FALLBACK UI HANDLER (Melayani Build Omni UI di /release/public) ---
	staticDir := "../release/public"
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// 🛡️ COOP/COEP Headers (SharedArrayBuffer + WASM support)
		w.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
		w.Header().Set("Cross-Origin-Embedder-Policy", "require-corp")
		w.Header().Set("Cross-Origin-Resource-Policy", "cross-origin")
		w.Header().Set("X-Powered-By", "OMNI-FRAMEWORK/2.0")

		path := filepath.Join(staticDir, r.URL.Path)
		// Periksa apakah file fisik tersedia
		_, err := os.Stat(path)
		if os.IsNotExist(err) || r.URL.Path == "/" {
			// SPA Routing: Jika pengguna mengakses URL React/Omni yang tidak ada
			http.ServeFile(w, r, filepath.Join(staticDir, "index.html"))
			return
		}
		// Berikan akses langsung untuk CSS, JS, Gambar dsb.
		http.ServeFile(w, r, path)
	})

	// Bungkus seluruh Router dengan CORS Middleware
	handlerDenganCORS := CORSMiddleware(mux)

	// Konfigurasi Server HTTP
	// Gunakan alamat dari AppConfig (host:port)
	serverAddr := core.GetServerAddr()

	srv := &http.Server{
		Addr:         serverAddr,
		Handler:      handlerDenganCORS,
		ReadTimeout:  time.Duration(core.AppConfig.Server.ReadTimeoutSeconds) * time.Second,
		WriteTimeout: time.Duration(core.AppConfig.Server.WriteTimeoutSeconds) * time.Second,
	}

	// ==========================================
	// KEMATIAN YANG TENANG (Graceful Shutdown)
	// ==========================================
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("🚨 Server gagal menyala: %v\n", err)
		}
	}()

	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("🛡️ %s v%s — SIAP TEMPUR!\n", core.AppConfig.AppName, core.AppConfig.Version)
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("  🌍 Environment            : %s\n", core.AppConfig.Environment)
	fmt.Printf("  📦 Max Upload             : %dGB\n", core.AppConfig.Storage.MaxUploadGB)
	fmt.Printf("  🏭 Worker Pool C++/Python : %d Pekerja\n", core.AppConfig.Engine.MaxConcurrentWorkers)
	fmt.Printf("  🏗️ Worker Pool Golang     : %d Pekerja\n", core.AppConfig.Engine.GoWorkers)
	fmt.Printf("  ⚙️  FFmpeg Threads         : %d\n", core.AppConfig.Engine.FFmpegThrottleThreads)
	fmt.Println("  🧹 Janitor Ephemeral      : Aktif")
	fmt.Printf("  🛡️ Rate Limiter           : %d req/s per IP\n", core.AppConfig.Security.RateLimitPerSecond)

	// NEXUS Cluster Banner
	nexusRoleBanner := strings.ToUpper(core.AppConfig.NexusCluster.Role)
	if nexusRoleBanner == "MASTER" {
		fmt.Println("  👑 NEXUS Cluster          : MASTER (Jenderal Armada)")
	} else if nexusRoleBanner == "WORKER" {
		fmt.Printf("  🪖 NEXUS Cluster          : WORKER → %s\n", core.AppConfig.NexusCluster.MasterURL)
	} else {
		fmt.Println("  ⚪ NEXUS Cluster          : STANDALONE")
	}

	fmt.Printf("  🚀 OMNI GATEWAY BERJALAN DI: http://%s\n", serverAddr)
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	// Tunggu sinyal mati dari OS (Ctrl+C / Docker Stop)
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)

	<-quit
	fmt.Println("\n🛑 Sinyal pemadaman diterima. Memulai Graceful Shutdown...")
	services.WriteLog("SYSTEM", "INFO", "Proses pemadaman server dimulai...")

	ctxShutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctxShutdown); err != nil {
		services.WriteLog("SYSTEM", "FATAL", fmt.Sprintf("Server mati paksa: %v", err))
		log.Fatal("Server forced to shutdown:", err)
	}

	// 🔥 Tutup koneksi Firebase Firestore
	core.CloseFirebase()

	fmt.Println("✅ OMNI TOOLS berhasil dimatikan tanpa meninggalkan Zombie Process. Sampai jumpa!")
}
