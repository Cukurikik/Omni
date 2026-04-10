// ============================================================
// 🚀 OMNI-NEXUS: Registry Server — Main Entry Point
// ============================================================
// Server HTTP utama untuk OMNI-NEXUS Package Registry.
// Menangani publish, search, download, dan stats.
//
// Jalankan: go run .
// Default:  http://localhost:9876
// ============================================================

package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func main() {
	// CLI flags
	port := flag.Int("port", 9876, "Port untuk NEXUS registry server")
	dataDir := flag.String("data", "./registry_data", "Direktori penyimpanan packages")
	flag.Parse()

	// Inisialisasi storage
	absDataDir, _ := filepath.Abs(*dataDir)
	storage := NewStorage(absDataDir)

	// Seed registry dari omni_modules jika ada
	// absDataDir = C:\Users\IKYY\Downloads\Omni\omni-runtime\nexus-registry\registry_data
	// repo root = C:\Users\IKYY\Downloads\Omni\omni-runtime
	repoRoot := filepath.Dir(filepath.Dir(absDataDir))
	modulesDir := filepath.Join(repoRoot, "omni_modules")
	if _, err := os.Stat(modulesDir); err == nil {
		seeded := SeedFromModules(storage, modulesDir)
		if seeded > 0 {
			fmt.Printf("🌱 Seeded %d packages dari %s\n\n", seeded, modulesDir)
		}
	}

	// Inisialisasi handlers
	handlers := NewHandlers(storage)

	// ============================================================
	// Router
	// ============================================================
	mux := http.NewServeMux()

	// Landing Page
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write([]byte(landingPageHTML()))
	})

	// API Routes
	mux.HandleFunc("/api/registry", handlers.HandleRegistry)
	mux.HandleFunc("/api/packages", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			handlers.HandlePublish(w, r)
		} else {
			handlers.HandleSearch(w, r)
		}
	})
	mux.HandleFunc("/api/packages/", func(w http.ResponseWriter, r *http.Request) {
		path := strings.TrimPrefix(r.URL.Path, "/api/packages/")
		parts := strings.SplitN(path, "/", 2)
		if len(parts) == 2 && parts[1] != "" {
			handlers.HandleGetVersion(w, r)
		} else {
			handlers.HandleGetPackage(w, r)
		}
	})
	mux.HandleFunc("/api/download/", handlers.HandleDownload)
	mux.HandleFunc("/api/search", handlers.HandleSearch)

	// Health check
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		respondJSON(w, 200, APIResponse{Success: true, Message: "OMNI-NEXUS is alive"})
	})

	// ============================================================
	// CORS Middleware
	// ============================================================
	handler := corsMiddleware(loggingMiddleware(mux))

	// ============================================================
	// Start Server
	// ============================================================
	addr := fmt.Sprintf(":%d", *port)
	server := &http.Server{
		Addr:         addr,
		Handler:      handler,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	printBanner(*port, absDataDir, storage)
	log.Fatal(server.ListenAndServe())
}

// ============================================================
// Middlewares
// ============================================================

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-OMNI-Token")

		if r.Method == "OPTIONS" {
			w.WriteHeader(204)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		elapsed := time.Since(start)
		fmt.Printf("[NEXUS] %s %s %s (%v)\n", r.Method, r.URL.Path, r.RemoteAddr, elapsed)
	})
}

// ============================================================
// Banner & Landing Page
// ============================================================

func printBanner(port int, dataDir string, storage *Storage) {
	stats := storage.Stats()

	fmt.Println("╔══════════════════════════════════════════════════════╗")
	fmt.Println("║                                                      ║")
	fmt.Println("║   🌌 OMNI-NEXUS REGISTRY SERVER v1.0.0               ║")
	fmt.Println("║   The Decentralized Package Registry for OMNI        ║")
	fmt.Println("║                                                      ║")
	fmt.Println("╚══════════════════════════════════════════════════════╝")
	fmt.Println()
	fmt.Printf("  🌐 Server     : http://localhost:%d\n", port)
	fmt.Printf("  📂 Storage    : %s\n", dataDir)
	fmt.Printf("  📦 Packages   : %d\n", stats.TotalPackages)
	fmt.Printf("  📊 Downloads  : %d\n", stats.TotalDownloads)
	fmt.Println()
	fmt.Println("  API Endpoints:")
	fmt.Println("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("  GET  /                     Landing page\n")
	fmt.Printf("  GET  /api/registry         Registry info & stats\n")
	fmt.Printf("  POST /api/packages         Publish package\n")
	fmt.Printf("  GET  /api/packages/{name}  Get package info\n")
	fmt.Printf("  GET  /api/search?q=...     Search packages\n")
	fmt.Printf("  GET  /api/download/{n}/{v} Download tarball\n")
	fmt.Printf("  GET  /health               Health check\n")
	fmt.Println("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Println()
	fmt.Println("  Menunggu koneksi...")
	fmt.Println()
}

func landingPageHTML() string {
	return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMNI-NEXUS — Package Registry</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 30%, #0d1b2a 70%, #0a0a1a 100%);
            color: #e0e0ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            padding: 40px;
            text-align: center;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 8px;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #a78bfa, #818cf8, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #8888cc;
            margin-bottom: 40px;
        }
        .search-box {
            display: flex;
            gap: 0;
            max-width: 600px;
            margin: 0 auto 40px;
        }
        .search-box input {
            flex: 1;
            padding: 14px 20px;
            font-size: 1rem;
            border: 2px solid #2d2d5e;
            border-right: none;
            border-radius: 12px 0 0 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            outline: none;
            transition: border-color 0.3s;
        }
        .search-box input:focus { border-color: #6366f1; }
        .search-box button {
            padding: 14px 28px;
            font-size: 1rem;
            border: 2px solid #6366f1;
            border-radius: 0 12px 12px 0;
            background: linear-gradient(135deg, #6366f1, #818cf8);
            color: #fff;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .search-box button:hover { transform: scale(1.05); }
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 40px;
        }
        .stat {
            text-align: center;
        }
        .stat .number {
            font-size: 2rem;
            font-weight: 700;
            color: #a78bfa;
        }
        .stat .label {
            font-size: 0.85rem;
            color: #6666aa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .commands {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 24px;
            text-align: left;
            margin-bottom: 30px;
        }
        .commands h3 {
            margin-bottom: 16px;
            color: #a78bfa;
        }
        .cmd {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 8px;
            padding: 10px 16px;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #c4b5fd;
        }
        .footer {
            margin-top: 40px;
            font-size: 0.8rem;
            color: #4444aa;
        }
        .footer a { color: #6366f1; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌌</div>
        <h1>OMNI-NEXUS</h1>
        <p class="subtitle">The Decentralized Package Registry for OMNI Framework</p>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Cari package... (contoh: omni-fs-core)" />
            <button onclick="searchPkg()">Cari</button>
        </div>

        <div class="stats" id="stats">
            <div class="stat"><div class="number" id="totalPkg">—</div><div class="label">Packages</div></div>
            <div class="stat"><div class="number" id="totalVer">—</div><div class="label">Versions</div></div>
            <div class="stat"><div class="number" id="totalDL">—</div><div class="label">Downloads</div></div>
        </div>

        <div class="commands">
            <h3>⚡ Quick Start</h3>
            <div class="cmd">$ omni get &lt;package-name&gt;</div>
            <div class="cmd">$ omni publish</div>
            <div class="cmd">$ omni search &lt;query&gt;</div>
        </div>

        <div id="results"></div>

        <div class="footer">
            Powered by <a href="https://omniframework.dev">OMNI Framework</a> — 15 Languages, One Runtime
        </div>
    </div>

    <script>
        fetch('/api/registry')
            .then(r => r.json())
            .then(d => {
                if (d.success && d.data.stats) {
                    document.getElementById('totalPkg').textContent = d.data.stats.total_packages;
                    document.getElementById('totalVer').textContent = d.data.stats.total_versions;
                    document.getElementById('totalDL').textContent = d.data.stats.total_downloads;
                }
            });

        function searchPkg() {
            const q = document.getElementById('searchInput').value;
            fetch('/api/search?q=' + encodeURIComponent(q))
                .then(r => r.json())
                .then(d => {
                    const el = document.getElementById('results');
                    if (d.success && d.data.packages) {
                        el.innerHTML = d.data.packages.map(p =>
                            '<div class="cmd">' + p.name + '@' + p.version + ' — ' + (p.description||'') + '</div>'
                        ).join('') || '<p style="color:#888">Tidak ada hasil.</p>';
                    }
                });
        }

        document.getElementById('searchInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') searchPkg();
        });
    </script>
</body>
</html>`
}
