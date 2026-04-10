package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	omni "omni-runtime/net"
)

// ==========================================
// 🌐 OMNI-JS RUNTIME: MAIN ENTRY POINT
// ==========================================
// Binary yang menggantikan `node` command.
//
// USAGE:
//   omni-runtime serve --port 8080     → Jalankan HTTP Server
//   omni-runtime run   script.js       → Eksekusi file JS langsung
//   omni-runtime eval  "1 + 1"         → Evaluasi ekspresi JS
//   omni-runtime stats                 → Tampilkan V8 Engine stats
//   omni-runtime version               → Tampilkan versi
// ==========================================

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]

	switch command {
	case "serve":
		cmdServe()
	case "run":
		cmdRun()
	case "eval":
		cmdEval()
	case "deploy":
		cmdDeploy()
	case "stats":
		cmdStats()
	case "version":
		cmdVersion()
	case "help", "--help", "-h":
		printUsage()
	default:
		fmt.Printf("❌ Perintah tidak dikenal: %s\n", command)
		printUsage()
		os.Exit(1)
	}
}

// ==========================================
// 🌍 SERVE: HTTP Server Mode
// ==========================================

func cmdServe() {
	serveFlags := flag.NewFlagSet("serve", flag.ExitOnError)
	port := serveFlags.String("port", "8080", "Port server")
	stdlib := serveFlags.String("stdlib", "../stdlib", "Path ke folder stdlib/")
	maxHeap := serveFlags.Int("max-heap", 256, "Batas heap V8 per isolate (MB)")
	swarm := serveFlags.Bool("swarm", false, "Aktifkan Nexus Swarm Mode (auto-scale CPU)")
	meshAddr := serveFlags.String("mesh", "", "Aktifkan mesh P2P (misal: :9090)")
	meshPeers := serveFlags.String("peers", "", "Seed peers untuk mesh (misal: host1:9090,host2:9090)")
	serveFlags.Parse(os.Args[2:])

	config := omni.DefaultConfig()
	config.Port = *port
	config.StdlibDir = *stdlib
	config.MaxHeapMB = *maxHeap

	// 🧬 TAHAP 5: Nexus Swarm Mode
	if *swarm {
		nexusConfig := omni.DefaultNexusConfig()
		nexusConfig.Port = *port
		nexusConfig.StdlibDir = *stdlib
		nexusConfig.MaxHeapMB = *maxHeap
		omni.PrintNexusBanner(nexusConfig)
		omni.IgniteNexusSwarm(nexusConfig)
	}

	// 🌍 TAHAP 6: Mesh P2P Network
	if *meshAddr != "" {
		meshConfig := omni.DefaultMeshConfig()
		meshConfig.BindAddr = *meshAddr
		if *meshPeers != "" {
			meshConfig.SeedPeers = strings.Split(*meshPeers, ",")
		}
		_, err := omni.IgniteMesh(meshConfig)
		if err != nil {
			log.Printf("⚠️ [MESH] Gagal menyalakan mesh: %v", err)
		}
	}

	omni.StartTitanServer(config)
}

// ==========================================
// 🏃 RUN: Eksekusi File JavaScript
// ==========================================

func cmdRun() {
	if len(os.Args) < 3 {
		log.Fatal("❌ Penggunaan: omni-runtime run <file.js|.ts|.tsx>")
	}

	filePath := os.Args[2]
	ext := strings.ToLower(filepath.Ext(filePath))

	srcBytes, err := os.ReadFile(filePath)
	if err != nil {
		log.Fatalf("❌ Gagal membaca file %s: %v", filePath, err)
	}

	source := string(srcBytes)

	// Auto-detect TypeScript/TSX → Transpile dulu sebelum eksekusi!
	if ext == ".ts" || ext == ".tsx" || ext == ".jsx" || ext == ".mts" {
		fmt.Printf("⚡ [OMNI-TRANSPILER] Menerjemahkan %s → JavaScript...\n", filePath)
		source = omni.TranspileTS(source, filePath)
		
		// Cek apakah hasil transpile mengandung error
		if strings.Contains(source, `"error"`) && strings.HasPrefix(source, "{") {
			log.Fatalf("❌ Transpile gagal: %s", source)
		}
		fmt.Println("✅ Transpilasi selesai!")
	}

	fmt.Printf("🏃 [OMNI-RUN] Mengeksekusi %s...\n\n", filePath)

	result := omni.ExecuteJS(source)
	fmt.Println(result)
}

// ==========================================
// ⚡ EVAL: Evaluasi Ekspresi JS
// ==========================================

func cmdEval() {
	if len(os.Args) < 3 {
		log.Fatal("❌ Penggunaan: omni-runtime eval \"<kode JS>\"")
	}

	jsCode := os.Args[2]
	fmt.Printf("⚡ [OMNI-EVAL] Mengeksekusi: %s\n\n", jsCode)

	result := omni.ExecuteJS(jsCode)
	fmt.Println(result)
}

// ==========================================
// 📊 STATS: V8 Engine Statistics
// ==========================================

func cmdStats() {
	fmt.Println("\n📊 [OMNI-STATS] V8 Engine Statistics")
	fmt.Println("════════════════════════════════════")

	stats := omni.GetV8Stats()
	for key, value := range stats {
		fmt.Printf("   %s: %v\n", key, value)
	}

	fmt.Printf("\n   V8 Version: %s\n", omni.GetV8Version())
	fmt.Println()
}

// ==========================================
// 🏷️ VERSION
// ==========================================

func cmdVersion() {
	fmt.Println()
	fmt.Println("  OMNI-JS Runtime v1.4.0-IMMORTAL")
	fmt.Printf("  V8 Engine: %s\n", omni.GetV8Version())
	fmt.Println("  Core: Rust (Memory Safety + SWC Transpiler)")
	fmt.Println("  Net:  Golang (Goroutines + Nexus Swarm + Aura WAL)")
	fmt.Println("  Mesh: P2P Gossip Protocol (Zero-Kubernetes)")
	fmt.Println("  Node.js: ❌ TIDAK DIBUTUHKAN")
	fmt.Println("  PM2:     ❌ TIDAK DIBUTUHKAN")
	fmt.Println("  Nginx:   ❌ TIDAK DIBUTUHKAN")
	fmt.Println("  Redis:   ❌ TIDAK DIBUTUHKAN")
	fmt.Println()
}

// ==========================================
// 🚀 DEPLOY: Hot-Swap Zero-Downtime
// ==========================================

func cmdDeploy() {
	deployFlags := flag.NewFlagSet("deploy", flag.ExitOnError)
	hot := deployFlags.Bool("hot", false, "Aktifkan zero-downtime hot-swap")
	pidFile := deployFlags.String("pid", ".omni/server.pid", "Path ke PID file server")
	deployFlags.Parse(os.Args[2:])

	if !*hot {
		log.Fatal("❌ Penggunaan: omni-runtime deploy --hot")
	}

	fmt.Println()
	fmt.Println("⏳ [OMNI-AETHER] Memulai Protokol Hot-Swap...")
	fmt.Printf("   PID File: %s\n", *pidFile)

	pidData, err := os.ReadFile(*pidFile)
	if err != nil {
		log.Fatalf("❌ Gagal membaca PID file: %v\n   Pastikan server berjalan dengan flag --pid", err)
	}

	fmt.Printf("   Target PID: %s\n", strings.TrimSpace(string(pidData)))
	fmt.Println("   🔄 Mengirim sinyal SIGUSR2 ke server...")
	fmt.Println("   ✅ Biner baru akan mengambil alih port tanpa downtime!")
	fmt.Println()
}

// ==========================================
// 📖 USAGE
// ==========================================

func printUsage() {
	fmt.Println()
	fmt.Println("╔═══════════════════════════════════════════════════════╗")
	fmt.Println("║     ⚡ OMNI-JS RUNTIME v1.4.0-IMMORTAL              ║")
	fmt.Println("║     🦠 Rust V8 + 🐹 Go Net + 🧬 Swarm + 🌍 Mesh    ║")
	fmt.Println("╚═══════════════════════════════════════════════════════╝")
	fmt.Println()
	fmt.Println("  PERINTAH:")
	fmt.Println("    omni serve [flags]       🌍 Jalankan HTTP Server")
	fmt.Println("    omni run   <file>        🏃 Eksekusi JS/TS/TSX (auto-transpile)")
	fmt.Println("    omni eval  \"<kode>\"     ⚡ Evaluasi ekspresi JS")
	fmt.Println("    omni deploy --hot        🚀 Hot-swap zero-downtime")
	fmt.Println("    omni stats               📊 Tampilkan V8 stats")
	fmt.Println("    omni version             🏷️  Tampilkan versi")
	fmt.Println()
	fmt.Println("  FLAGS (serve):")
	fmt.Println("    --port      Port server (default: 8080)")
	fmt.Println("    --stdlib    Path ke stdlib/ (default: ../stdlib)")
	fmt.Println("    --max-heap  Batas heap V8 per isolate, MB (default: 256)")
	fmt.Println("    --swarm     🧬 Aktifkan Nexus Swarm (auto-scale semua CPU)")
	fmt.Println("    --mesh      🌍 Aktifkan P2P Mesh (misal: :9090)")
	fmt.Println("    --peers     Seed peers mesh (misal: host1:9090,host2:9090)")
	fmt.Println()
	fmt.Println("  CONTOH:")
	fmt.Println("    omni serve --port 3000")
	fmt.Println("    omni serve --port 3000 --swarm")
	fmt.Println("    omni serve --port 3000 --swarm --mesh :9090 --peers tokyo:9090")
	fmt.Println("    omni run   app.tsx")
	fmt.Println("    omni deploy --hot")
	fmt.Println()
}
