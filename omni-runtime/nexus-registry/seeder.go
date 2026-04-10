// ============================================================
// 🌱 OMNI-NEXUS: Seeder — Pre-populate registry
// ============================================================
// Berjalan sebelum server start untuk mendaftarkan modul-modul
// dari omni_modules/ ke registry storage.
// ============================================================

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// SeedFromModules memindai omni_modules/ dan mendaftarkan
// setiap modul sebagai package ke storage registry.
func SeedFromModules(storage *Storage, modulesDir string) int {
	entries, err := os.ReadDir(modulesDir)
	if err != nil {
		return 0
	}

	seeded := 0
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}

		name := entry.Name()

		// Cek apakah modul sudah ada di registry
		if _, err := storage.GetPackage(name); err == nil {
			continue // Skip yang sudah ada
		}

		// Buat deskripsi berdasarkan nama
		desc := generateDescription(name)

		// Hitung file sumber sebagai proxy ukuran
		sourceCount := countSources(filepath.Join(modulesDir, name))

		// Buat fake tarball data (header + metadata)
		tarball := createFakeTarball(name, "1.0.0", sourceCount)

		req := PublishRequest{
			Name:        name,
			Version:     "1.0.0",
			Description: desc,
			Authors:     []string{"OMNI Core Team <core@omniframework.dev>"},
			License:     "MIT",
			Homepage:    fmt.Sprintf("https://omniframework.dev/packages/%s", name),
			Repository:  fmt.Sprintf("https://github.com/omni-framework/%s", name),
			Keywords:    extractKeywords(name),
			Edition:     "omni-2025",
		}

		if _, err := storage.Publish(req, tarball); err == nil {
			seeded++
		}
	}

	return seeded
}

func generateDescription(name string) string {
	// Hapus prefix "omni-"
	core := strings.TrimPrefix(name, "omni-")
	parts := strings.Split(core, "-")

	descriptions := map[string]string{
		"fs-core":        "High-performance filesystem I/O with POSIX syscalls and async watchers",
		"events":         "Lock-free event emitter and pub/sub system with zero-copy dispatch",
		"buffer":         "Zero-copy binary buffer with endian-aware read/write operations",
		"net-tcp":        "Native TCP server and client with goroutine-based concurrency",
		"http2":          "HTTP/2 server with middleware pipeline (Logger, CORS, Recovery)",
		"crypto":         "Cryptographic primitives: AES-256-GCM, SHA-256, Ed25519, X25519",
		"json":           "Ultra-fast JSON parser and serializer with streaming support",
		"yaml":           "YAML parser and emitter with full 1.2 spec compliance",
		"xml":            "Streaming XML parser with namespace-aware DOM builder",
		"sqlite":         "Embedded SQLite3 database driver with connection pooling",
		"postgres":       "PostgreSQL wire-protocol client with async query pipeline",
		"redis":          "Redis client with cluster support and Lua scripting bridge",
		"websocket":      "WebSocket server/client with compression and auto-reconnect",
		"webrtc":         "WebRTC data channel and peer connection management",
		"stream-io":      "Streaming I/O primitives: Transform, Pipeline, Multiplex",
		"process":        "Child process spawning with IPC and signal handling",
		"timers":         "High-resolution timers with tick-based scheduler",
		"tty":            "Terminal I/O: raw mode, ANSI colors, cursor control",
		"readline":       "Interactive line editor with history and tab completion",
		"url":            "URL parser and builder with full RFC 3986 compliance",
		"querystring":    "Query string parser and encoder with nested object support",
		"session":        "Session management with pluggable stores (memory, Redis, FS)",
		"logger":         "Structured logger with levels, rotation, and JSON output",
		"vm":             "Virtual machine for OMNI bytecode execution",
		"allocator":      "Custom memory allocator: arena, pool, and slab strategies",
		"repl":           "Interactive REPL with syntax highlighting and completion",
		"profiler":       "CPU and memory profiler with flamegraph export",
		"debugger":       "Step-through debugger with breakpoints and watch expressions",
		"test-runner":    "Test framework with describe/it blocks and assertion library",
		"test-mock":      "Mocking library with spy, stub, and fake generators",
		"test-coverage":  "Code coverage analyzer with per-line and branch metrics",
		"bench-suite":    "Benchmarking suite with statistical analysis and comparison",
		"ai":             "AI inference runtime with ONNX and TensorFlow Lite support",
		"ai-tensors":     "Tensor operations: matmul, conv2d, softmax on CPU/GPU",
		"ai-sandbox":     "Sandboxed AI model execution environment",
		"wasm-packager":  "WebAssembly module bundler and optimizer",
		"edge-runtime":   "Edge compute runtime with V8 isolates and cold-start <5ms",
		"v8-isolate":     "V8 JavaScript engine integration with isolate management",
		"web3-core":      "Web3 primitives: wallet, transaction signing, ABI encoding",
		"ui":             "UI component renderer for OMNI declarative templates",
	}

	if desc, ok := descriptions[core]; ok {
		return desc
	}

	// Fallback: generate dari nama
	for i, p := range parts {
		parts[i] = strings.Title(p)
	}
	return fmt.Sprintf("OMNI %s module for the polyglot runtime ecosystem", strings.Join(parts, " "))
}

func extractKeywords(name string) []string {
	core := strings.TrimPrefix(name, "omni-")
	parts := strings.Split(core, "-")
	keywords := []string{"omni", "runtime"}
	keywords = append(keywords, parts...)
	return keywords
}

func countSources(dir string) int {
	count := 0
	filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}
		ext := filepath.Ext(path)
		switch ext {
		case ".c", ".cpp", ".rs", ".go", ".omni":
			count++
		}
		return nil
	})
	return count
}

func createFakeTarball(name, version string, sourceCount int) []byte {
	// Buat tarball "semantik" — bukan gzip asli, tapi metadata payload
	// yang cukup untuk registry tracking
	manifest := map[string]interface{}{
		"name":         name,
		"version":      version,
		"source_files": sourceCount,
		"edition":      "omni-2025",
		"runtime":      "llvm-omni",
	}
	data, _ := json.MarshalIndent(manifest, "", "  ")

	// Prefix dengan magic bytes
	payload := []byte("OMNI-PKG-V1\n")
	payload = append(payload, data...)

	// Pad to realistic size
	padding := make([]byte, sourceCount*1024)
	payload = append(payload, padding...)

	return payload
}
