// ==========================================
// 🛡️ OMNI-BRIDGE: STUB (No-CGO Fallback)
// ==========================================
// File ini aktif HANYA jika CGO dimatikan (CGO_ENABLED=0)
// atau saat GCC/MinGW tidak tersedia (Windows tanpa toolchain).
//
// Fungsi-fungsi di sini meng-mirror semua fungsi di omni_bridge.go,
// tapi mengembalikan pesan error yang jelas alih-alih crash.
//
// Tujuan:
//   1. Kode tetap bisa di-compile dan di-lint pada Windows
//   2. IDE (VS Code / GoLand) tidak menampilkan error merah
//   3. Developer bisa menguji logika routing/serve tanpa Rust core
//
// Untuk mengaktifkan mode FULL (Rust V8 Engine), install:
//   - MinGW-w64 (Windows) atau GCC (Linux/Mac)
//   - Set CGO_ENABLED=1
//   - cargo build --release (di folder core/)
// ==========================================

//go:build !cgo

package net

import (
	"fmt"
	"log"
	"strings"
)

const stubWarning = "⚠️ [OMNI-BRIDGE] CGO DISABLED — V8 Engine tidak aktif. Install GCC/MinGW dan set CGO_ENABLED=1"

func init() {
	log.Println(stubWarning)
}

// ExecuteJS stub — kembalikan pesan bahwa V8 tidak aktif
func ExecuteJS(jsCode string) string {
	return fmt.Sprintf(`{"error": "V8 Engine tidak aktif (CGO_ENABLED=0)", "stub": true, "input_length": %d}`, len(jsCode))
}

// ExecuteWithContext stub
func ExecuteWithContext(jsCode, method, url, headers, body string) string {
	return fmt.Sprintf(`{"error": "V8 Engine tidak aktif (CGO_ENABLED=0)", "stub": true, "method": "%s", "url": "%s"}`, method, url)
}

// ExecuteSandboxed stub
func ExecuteSandboxed(jsCode string, maxHeapMB int) string {
	return fmt.Sprintf(`{"error": "V8 Engine tidak aktif (CGO_ENABLED=0)", "stub": true, "max_heap_mb": %d}`, maxHeapMB)
}

// GetV8Stats stub — kembalikan stats kosong
func GetV8Stats() map[string]interface{} {
	return map[string]interface{}{
		"mode":         "STUB (No CGO)",
		"v8_active":    false,
		"heap_used":    0,
		"heap_total":   0,
		"warning":      stubWarning,
	}
}

// GetV8Version stub
func GetV8Version() string {
	return "STUB-MODE (V8 tidak tersedia — CGO_ENABLED=0)"
}

// TranspileTS stub — tanpa SWC Rust, kembalikan kode apa adanya
// dengan stripping type annotations secara sederhana (regex-based fallback)
func TranspileTS(tsCode, filename string) string {
	log.Printf("⚠️ [STUB-TRANSPILER] Transpiling %s tanpa SWC (fallback mode)", filename)
	// Basic type stripping: hapus `: type` annotations
	// Ini BUKAN pengganti SWC, tapi cukup untuk development/testing
	result := tsCode
	// Hapus type imports
	result = stripPattern(result, "import type ")
	// Hapus interface declarations  
	result = stripInterfaceBlocks(result)
	return result
}

// NeedsTranspile stub — cek ekstensi saja
func NeedsTranspile(filename string) bool {
	lower := strings.ToLower(filename)
	return strings.HasSuffix(lower, ".ts") ||
		strings.HasSuffix(lower, ".tsx") ||
		strings.HasSuffix(lower, ".jsx") ||
		strings.HasSuffix(lower, ".mts")
}

// TranspileAndExecute stub
func TranspileAndExecute(tsCode, filename string) string {
	js := TranspileTS(tsCode, filename)
	return ExecuteJS(js)
}

// stripPattern menghapus baris yang mengandung pattern tertentu
func stripPattern(code, pattern string) string {
	var lines []string
	for _, line := range strings.Split(code, "\n") {
		if !strings.Contains(line, pattern) {
			lines = append(lines, line)
		}
	}
	return strings.Join(lines, "\n")
}

// stripInterfaceBlocks menghapus blok interface/type sederhana
func stripInterfaceBlocks(code string) string {
	var result []string
	inBlock := false
	braceCount := 0

	for _, line := range strings.Split(code, "\n") {
		trimmed := strings.TrimSpace(line)

		if !inBlock {
			if strings.HasPrefix(trimmed, "interface ") || strings.HasPrefix(trimmed, "type ") {
				if strings.Contains(trimmed, "{") {
					inBlock = true
					braceCount = strings.Count(trimmed, "{") - strings.Count(trimmed, "}")
					if braceCount <= 0 {
						inBlock = false
					}
				}
				continue // Skip interface/type line
			}
			result = append(result, line)
		} else {
			braceCount += strings.Count(trimmed, "{") - strings.Count(trimmed, "}")
			if braceCount <= 0 {
				inBlock = false
			}
		}
	}

	return strings.Join(result, "\n")
}
