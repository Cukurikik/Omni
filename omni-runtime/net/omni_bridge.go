// ==========================================
// ⚡ OMNI-BRIDGE: REAL IMPLEMENTATION (CGO Required)
// ==========================================
// File ini HANYA aktif jika CGO_ENABLED=1 dan GCC/MinGW tersedia.
// Jika CGO tidak tersedia, omni_bridge_stub.go yang aktif.
// ==========================================

//go:build cgo

package net

/*
// ==========================================
// ⚡ OMNI-BRIDGE: Jembatan Kedaulatan (Golang ↔ Rust)
// ==========================================
// CGO mengikat memori Golang dengan Library Rust (libomni_core).
// Setiap fungsi C extern yang di-deklarasikan di sini sesuai
// dengan fungsi #[no_mangle] extern "C" di Rust lib.rs.
//
// ALUR KOMUNIKASI:
//   1. Golang menerima HTTP Request dari Browser
//   2. Golang membaca file JavaScript dari SSD (Bare-Metal I/O)
//   3. Golang mengirim string JS ke Rust via CGO pointer
//   4. Rust mengeksekusi JS di V8 Sandbox (JIT compiled)
//   5. Rust mengembalikan hasil sebagai C-String
//   6. Golang mengirim hasil ke Browser sebagai HTTP Response
//
// KEAMANAN MEMORI:
//   - Setiap C.CString WAJIB di-free dengan defer C.free()
//   - Setiap hasil dari Rust WAJIB di-free dengan C.omni_free_string()
//   - Jika pointer NULL, Rust mengembalikan JSON error
// ==========================================

// Platform-aware linking:
// Windows: -lomni_core + Windows system libs (no -ldl/-lpthread)
// Linux/Mac: -lomni_core + POSIX libs (-ldl -lm -lpthread)
#cgo windows LDFLAGS: -L../core/target/release -lomni_core -lws2_32 -lntdll -luserenv -lbcrypt
#cgo linux LDFLAGS: -L../core/target/release -lomni_core -ldl -lm -lpthread
#cgo darwin LDFLAGS: -L../core/target/release -lomni_core -ldl -lm -lpthread
#include <stdlib.h>

// Fungsi FFI yang sudah kita buat di Rust (core/src/lib.rs)
extern char* omni_execute(const char* js_code);
extern char* omni_execute_with_context(
    const char* js_code,
    const char* method,
    const char* url,
    const char* headers,
    const char* body
);
extern char* omni_execute_sandboxed(const char* js_code, size_t max_heap_mb);
extern char* omni_get_stats();
extern char* omni_v8_version();
extern void  omni_free_string(char* ptr);

// TAHAP 3+4: Transpiler FFI (TypeScript/TSX → JavaScript)
extern char* omni_transpile(const char* ts_code, const char* filename);
extern char* omni_needs_transpile(const char* filename);
*/
import "C"
import (
	"encoding/json"
	"log"
	"unsafe"
)

// ==========================================
// 🚀 PUBLIC API: Dipanggil oleh server.go
// ==========================================

// ExecuteJS mengirim kode JavaScript murni ke V8 Sandbox via Rust FFI.
// Ini adalah cara PALING DASAR untuk mengeksekusi JS.
//
// Contoh:
//
//	result := net.ExecuteJS("1 + 1")  // → "2"
//	result := net.ExecuteJS(`JSON.stringify({ok: true})`)  // → '{"ok":true}'
func ExecuteJS(jsCode string) string {
	// Konversi Go string → C string (heap allocated, harus di-free)
	cCode := C.CString(jsCode)
	defer C.free(unsafe.Pointer(cCode))

	// 🚀 EKSEKUSI: Golang → Rust → V8 Engine
	cResult := C.omni_execute(cCode)
	defer C.omni_free_string(cResult) // WAJIB! Cegah memory leak

	return C.GoString(cResult)
}

// ExecuteWithContext mengeksekusi JavaScript dengan konteks HTTP Request.
// Ini adalah fungsi yang dipanggil oleh HTTP server untuk setiap request.
//
// Parameter:
//   - jsCode: Kode JavaScript developer (isi file .js)
//   - method: HTTP method (GET, POST, PUT, dll)
//   - url: URL path (/api/users, /dashboard, dll)
//   - headers: JSON string dari HTTP headers
//   - body: Request body (untuk POST/PUT)
//
// Contoh:
//
//	result := net.ExecuteWithContext(jsContent, "GET", "/api/users", "{}", "")
func ExecuteWithContext(jsCode, method, url, headers, body string) string {
	cCode := C.CString(jsCode)
	cMethod := C.CString(method)
	cURL := C.CString(url)
	cHeaders := C.CString(headers)
	cBody := C.CString(body)

	defer C.free(unsafe.Pointer(cCode))
	defer C.free(unsafe.Pointer(cMethod))
	defer C.free(unsafe.Pointer(cURL))
	defer C.free(unsafe.Pointer(cHeaders))
	defer C.free(unsafe.Pointer(cBody))

	// 🚀 EKSEKUSI SPEK DEWA: Go → Rust → C++ (V8)
	cResult := C.omni_execute_with_context(cCode, cMethod, cURL, cHeaders, cBody)
	defer C.omni_free_string(cResult)

	return C.GoString(cResult)
}

// ExecuteSandboxed mengeksekusi JavaScript dengan batas memori.
// Digunakan untuk kode untrusted (upload user, plugin pihak ketiga).
//
// Parameter:
//   - jsCode: Kode JavaScript
//   - maxHeapMB: Batas memori heap V8 dalam megabytes (0 = default 256MB)
func ExecuteSandboxed(jsCode string, maxHeapMB int) string {
	cCode := C.CString(jsCode)
	defer C.free(unsafe.Pointer(cCode))

	cResult := C.omni_execute_sandboxed(cCode, C.size_t(maxHeapMB))
	defer C.omni_free_string(cResult)

	return C.GoString(cResult)
}

// GetV8Stats mengembalikan statistik heap memory dari V8 Engine.
// Digunakan untuk monitoring dan Prometheus metrics.
func GetV8Stats() map[string]interface{} {
	cResult := C.omni_get_stats()
	defer C.omni_free_string(cResult)

	jsonStr := C.GoString(cResult)

	var stats map[string]interface{}
	if err := json.Unmarshal([]byte(jsonStr), &stats); err != nil {
		log.Printf("⚠️ [OMNI-BRIDGE] Gagal parse V8 stats: %v", err)
		return map[string]interface{}{"error": err.Error()}
	}

	return stats
}

// GetV8Version mengembalikan versi V8 Engine yang sedang berjalan.
func GetV8Version() string {
	cResult := C.omni_v8_version()
	defer C.omni_free_string(cResult)
	return C.GoString(cResult)
}

// ==========================================
// ⚡ TRANSPILER: TypeScript/TSX → JavaScript
// ==========================================

// TranspileTS mengkonversi TypeScript/TSX menjadi JavaScript murni
// menggunakan SWC Rust transpiler.
// Golang memanggil ini SEBELUM mengirim kode ke V8 Engine.
//
// Contoh:
//
//	js := net.TranspileTS(tsCode, "app.tsx")
//	result := net.ExecuteJS(js)
func TranspileTS(tsCode, filename string) string {
	cCode := C.CString(tsCode)
	cFilename := C.CString(filename)
	defer C.free(unsafe.Pointer(cCode))
	defer C.free(unsafe.Pointer(cFilename))

	cResult := C.omni_transpile(cCode, cFilename)
	defer C.omni_free_string(cResult)

	return C.GoString(cResult)
}

// NeedsTranspile cek apakah file perlu di-transpile berdasarkan ekstensi.
// Returns true untuk .ts, .tsx, .jsx, .mts
func NeedsTranspile(filename string) bool {
	cFilename := C.CString(filename)
	defer C.free(unsafe.Pointer(cFilename))

	cResult := C.omni_needs_transpile(cFilename)
	defer C.omni_free_string(cResult)

	return C.GoString(cResult) == "true"
}

// TranspileAndExecute adalah shortcut: Transpile TS → JS → Execute di V8.
// Ini adalah satu panggilan untuk workflow `omni run app.ts`.
func TranspileAndExecute(tsCode, filename string) string {
	js := TranspileTS(tsCode, filename)
	return ExecuteJS(js)
}
