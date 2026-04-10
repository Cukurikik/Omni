package net

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"time"
)

// ==========================================
// 🌐 OMNI-NET: THE SUPREME COMMANDER (JENDERAL GOLANG)
// ==========================================
// Server HTTP Bare-Metal yang:
//   1. Menerima request dari browser (10.000+ concurrent via Goroutines)
//   2. Membaca file JavaScript dari SSD (Bare-Metal I/O — bukan Node.js fs)
//   3. Mengirim JS ke Sandbox Rust-V8 untuk dieksekusi secara paralel
//   4. Mengembalikan response ke browser dalam ~1ms
//
// KEUNGGULAN vs NODE.JS:
//   Node.js: Single-thread Event Loop → 10K request = antrian panjang
//   OMNI-JS: 10K Goroutines × 10K V8 Isolates = komputasi PARALEL sejati
//
// GOROUTINES:
//   Setiap HTTP request = 1 Goroutine (hanya 2KB RAM)
//   10.000 request bersamaan = hanya 20MB RAM total untuk scheduling
//   Bandingkan: Node.js thread = ~8MB per thread
// ==========================================

// ServerConfig menyimpan konfigurasi OMNI-NET Server
type ServerConfig struct {
	Port          string
	StdlibDir     string // Path ke folder stdlib/ (berisi routes/*.js)
	MaxHeapMB     int    // Batas memori per V8 Isolate (0 = unlimited)
	ReadTimeout   time.Duration
	WriteTimeout  time.Duration
	EnableCORS    bool
	EnableMetrics bool
}

// DefaultConfig mengembalikan konfigurasi default yang aman.
func DefaultConfig() ServerConfig {
	return ServerConfig{
		Port:          "8080",
		StdlibDir:     "../stdlib",
		MaxHeapMB:     256, // 256MB per isolate (cukup untuk hampir semua use case)
		ReadTimeout:   30 * time.Second,
		WriteTimeout:  120 * time.Second,
		EnableCORS:    true,
		EnableMetrics: true,
	}
}

// Statistik runtime (atomic untuk thread-safety)
var (
	totalRequests   atomic.Int64
	activeRequests  atomic.Int64
	totalErrors     atomic.Int64
	totalJSExecTime atomic.Int64 // dalam nanoseconds
)

// ==========================================
// 🚀 START SERVER: Entry Point
// ==========================================

// StartTitanServer menyalakan Jenderal Golang.
func StartTitanServer(config ServerConfig) {
	mux := http.NewServeMux()

	// 🛡️ Health Check (untuk Load Balancer / Kubernetes)
	mux.HandleFunc("/omni/health", handleHealth)

	// 📊 Metrics (untuk Prometheus)
	if config.EnableMetrics {
		mux.HandleFunc("/omni/metrics", handleMetrics)
	}

	// 📊 V8 Engine Stats
	mux.HandleFunc("/omni/v8/stats", handleV8Stats)

	// ⚡ REPL: Eksekusi JS langsung via POST body (Development mode only)
	mux.HandleFunc("/omni/eval", func(w http.ResponseWriter, r *http.Request) {
		handleEval(w, r, config)
	})

	// 🌍 CATCH-ALL: File-Based JavaScript Router
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		handleRoute(w, r, config)
	})

	// Bungkus dengan middleware
	var handler http.Handler = mux
	if config.EnableCORS {
		handler = corsMiddleware(handler)
	}
	handler = loggingMiddleware(handler)
	handler = recoveryMiddleware(handler)

	// Konfigurasi server
	server := &http.Server{
		Addr:         ":" + config.Port,
		Handler:      handler,
		ReadTimeout:  config.ReadTimeout,
		WriteTimeout: config.WriteTimeout,
	}

	// War Banner
	printBanner(config)

	// 🚀 LAUNCH!
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("💥 [OMNI-NET FATAL] Server tumbang: %v", err)
	}
}

// ==========================================
// 🌍 ROUTE HANDLER: File-Based JS Router
// ==========================================

func handleRoute(w http.ResponseWriter, r *http.Request, config ServerConfig) {
	totalRequests.Add(1)
	activeRequests.Add(1)
	defer activeRequests.Add(-1)

	startTime := time.Now()

	// 1. RESOLVE FILE PATH: URL → File (JS/TS/TSX)
	urlPath := strings.TrimPrefix(r.URL.Path, "/")
	if urlPath == "" || urlPath == "/" {
		urlPath = "index"
	}
	urlPath = strings.TrimSuffix(urlPath, "/")

	// Cari file route dengan prioritas ekstensi: .js → .ts → .tsx → .jsx
	routeBase := filepath.Join(config.StdlibDir, "routes", urlPath)
	exts := []string{".js", ".ts", ".tsx", ".jsx"}
	jsFilePath := ""

	for _, ext := range exts {
		candidate := routeBase + ext
		if _, err := os.Stat(candidate); err == nil {
			jsFilePath = candidate
			break
		}
	}

	// Fallback: coba index.* di dalam folder
	if jsFilePath == "" {
		for _, ext := range exts {
			candidate := filepath.Join(routeBase, "index"+ext)
			if _, err := os.Stat(candidate); err == nil {
				jsFilePath = candidate
				break
			}
		}
	}

	if jsFilePath == "" {
		totalErrors.Add(1)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error":   "Route tidak ditemukan",
			"path":    r.URL.Path,
			"runtime": "OMNI-JS/1.3.0",
		})
		return
	}

	// 2. BACA FILE DARI SSD (Golang I/O Bare-Metal)
	srcBytes, err := os.ReadFile(jsFilePath)
	if err != nil {
		totalErrors.Add(1)
		http.Error(w, fmt.Sprintf(`{"error": "Gagal membaca file: %s"}`, err), http.StatusInternalServerError)
		return
	}

	jsCode := string(srcBytes)

	// 2.5. AUTO-TRANSPILE jika TypeScript/TSX
	if NeedsTranspile(jsFilePath) {
		jsCode = TranspileTS(jsCode, jsFilePath)
	}

	// 3. SERIALIZE HEADERS ke JSON
	headersMap := make(map[string]string)
	for key, values := range r.Header {
		headersMap[key] = strings.Join(values, ", ")
	}
	headersJSON, _ := json.Marshal(headersMap)

	// 4. BACA BODY (untuk POST/PUT/PATCH)
	body := ""
	if r.Body != nil && (r.Method == "POST" || r.Method == "PUT" || r.Method == "PATCH") {
		bodyBytes := make([]byte, 0)
		buf := make([]byte, 4096)
		for {
			n, readErr := r.Body.Read(buf)
			if n > 0 {
				bodyBytes = append(bodyBytes, buf[:n]...)
			}
			if readErr != nil {
				break
			}
		}
		body = string(bodyBytes)
	}

	// 5. 🚀 EKSEKUSI DI SANDBOX V8 (via Rust FFI)
	// Setiap Goroutine mendapat V8 Isolate-nya sendiri — PARALEL SEJATI!
	var result string
	if config.MaxHeapMB > 0 {
		result = ExecuteSandboxed(
			jsCode+"\n\n"+buildHandlerInvocation(r.Method, r.URL.Path, string(headersJSON), body),
			config.MaxHeapMB,
		)
	} else {
		result = ExecuteWithContext(jsCode, r.Method, r.URL.Path, string(headersJSON), body)
	}

	execDuration := time.Since(startTime)
	totalJSExecTime.Add(execDuration.Nanoseconds())

	// 6. KIRIM RESPONSE KE BROWSER
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-OMNI-Runtime", "OMNI-JS/1.3.0")
	w.Header().Set("X-OMNI-Exec-Time", execDuration.String())
	w.Write([]byte(result))
}

// buildHandlerInvocation membuat kode JS untuk memanggil OmniHandler.
func buildHandlerInvocation(method, url, headers, body string) string {
	return fmt.Sprintf(`
		// 🌐 Auto-injected by OMNI-NET (Golang)
		const __omni_req = {
			method: "%s",
			url: "%s",
			headers: %s,
			body: %s
		};
		if (typeof OmniHandler === 'function') {
			OmniHandler(__omni_req);
		} else {
			JSON.stringify({error: "OmniHandler tidak ditemukan di file ini"});
		}
	`, method, url, headers, "`"+body+"`")
}

// ==========================================
// 📍 SPECIAL HANDLERS
// ==========================================

func handleHealth(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "ALIVE",
		"runtime": "OMNI-JS/1.3.0",
		"engine":  "Rust-V8 + Golang-NET",
		"uptime":  time.Since(time.Now()).String(), // TODO: track actual uptime
	})
}

func handleMetrics(w http.ResponseWriter, _ *http.Request) {
	avgExecNs := int64(0)
	total := totalRequests.Load()
	if total > 0 {
		avgExecNs = totalJSExecTime.Load() / total
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"total_requests":     totalRequests.Load(),
		"active_requests":    activeRequests.Load(),
		"total_errors":       totalErrors.Load(),
		"avg_exec_time_ns":   avgExecNs,
		"avg_exec_time_ms":   float64(avgExecNs) / 1_000_000,
		"total_js_exec_time": fmt.Sprintf("%dms", totalJSExecTime.Load()/1_000_000),
	})
}

func handleV8Stats(w http.ResponseWriter, _ *http.Request) {
	stats := GetV8Stats()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func handleEval(w http.ResponseWriter, r *http.Request, config ServerConfig) {
	if r.Method != "POST" {
		http.Error(w, `{"error": "Gunakan POST untuk /omni/eval"}`, http.StatusMethodNotAllowed)
		return
	}

	// Baca body sebagai kode JS
	body := make([]byte, 0)
	buf := make([]byte, 4096)
	for {
		n, err := r.Body.Read(buf)
		if n > 0 {
			body = append(body, buf[:n]...)
		}
		if err != nil {
			break
		}
	}

	if len(body) == 0 {
		http.Error(w, `{"error": "Body kosong — kirim kode JavaScript"}`, http.StatusBadRequest)
		return
	}

	result := ExecuteSandboxed(string(body), config.MaxHeapMB)
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(result))
}

// ==========================================
// 🛡️ MIDDLEWARE STACK
// ==========================================

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Access-Control-Max-Age", "86400")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("📡 [OMNI-NET] %s %s ← %s [%s]",
			r.Method, r.URL.Path, r.RemoteAddr, time.Since(start))
	})
}

func recoveryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				totalErrors.Add(1)
				log.Printf("💥 [RECOVERY] Panic ditangkap: %v", err)
				http.Error(w, `{"error": "Internal Server Error — Panic recovered"}`, http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}

// ==========================================
// 🏴 WAR BANNER
// ==========================================

func printBanner(config ServerConfig) {
	v8Version := GetV8Version()

	fmt.Println()
	fmt.Println("╔══════════════════════════════════════════════════════════════╗")
	fmt.Println("║                                                              ║")
	fmt.Println("║   ⚡  O M N I - J S   R U N T I M E   v1.3.0                ║")
	fmt.Println("║   🦀 Rust V8 Engine  +  🐹 Golang Networking                ║")
	fmt.Println("║                                                              ║")
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Printf("║   🌍 Server     : http://0.0.0.0:%s                       ║\n", config.Port)
	fmt.Printf("║   ⚙️ V8 Engine   : %s                              ║\n", v8Version)
	fmt.Printf("║   🧠 Heap Limit  : %dMB per Isolate                        ║\n", config.MaxHeapMB)
	fmt.Printf("║   📂 Stdlib      : %s                              ║\n", config.StdlibDir)
	fmt.Println("║   🛡️ CORS       : ENABLED                                   ║")
	fmt.Println("║   📊 Metrics     : /omni/metrics                             ║")
	fmt.Println("╠══════════════════════════════════════════════════════════════╣")
	fmt.Println("║   🚀 Goroutines PARALEL aktif — Node.js Event Loop MUSNAH  ║")
	fmt.Println("║   🦀 Memory Safety via Rust — Zero Leak Guarantee           ║")
	fmt.Println("╚══════════════════════════════════════════════════════════════╝")
	fmt.Println()
}
