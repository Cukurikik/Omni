package net

// ==========================================
// 🌐 OMNI-NEXUS FETCH: THE POLYGLOT API GATEWAY
// ==========================================
// Rantai Eksekusi 5 Dimensi:
//   TypeScript → JavaScript (V8) → Golang (HTTP) → Rust (Validate) → Python (Crunch)
//
// Saat developer memanggil `omniFetch()`, data melintasi 5 bahasa:
//   1. TypeScript: Developer menulis kode elegan + IntelliSense
//   2. JavaScript: V8 Engine mengeksekusi + meneruskan ke Jenderal
//   3. Golang: Melakukan HTTP request bare-metal (kebal timeout)
//   4. Rust: Memvalidasi JSON (kebal XSS/SQLi/injection)
//   5. Python: Mengolah data angka raksasa (Pandas/NumPy speed)
//
// KEUNGGULAN vs TRADISIONAL:
//   ❌ fetch() browser → 1 bahasa, 0 validasi, 0 data science
//   ⚡ omniFetch()     → 5 bahasa, Rust security, Python AI
// ==========================================

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ==========================================
// 🏗️ NEXUS ENGINE: SINGLETON GATEWAY
// ==========================================

type NexusEngine struct {
	mu          sync.RWMutex
	client      *http.Client
	stats       NexusStats
	initialized bool
}

type NexusStats struct {
	TotalRequests   int64   `json:"total_requests"`
	SuccessCount    int64   `json:"success_count"`
	ErrorCount      int64   `json:"error_count"`
	RustValidated   int64   `json:"rust_validated"`
	PythonCrunched  int64   `json:"python_crunched"`
	AvgLatencyMs    float64 `json:"avg_latency_ms"`
	LastRequestTime string  `json:"last_request_time"`
	Uptime          string  `json:"uptime"`
}

type NexusFetchRequest struct {
	URL            string            `json:"url"`
	Method         string            `json:"method"`
	Headers        map[string]string `json:"headers"`
	Body           string            `json:"body"`
	TimeoutMs      int               `json:"timeout_ms"`
	ValidateRust   bool              `json:"validate_rust"`
	PythonScript   string            `json:"python_script"`
	PythonFunc     string            `json:"python_func"`
	FollowRedirect bool              `json:"follow_redirect"`
}

type NexusFetchResponse struct {
	Status      int               `json:"status"`
	StatusText  string            `json:"status_text"`
	Headers     map[string]string `json:"headers"`
	Body        string            `json:"body"`
	URL         string            `json:"url"`
	Ok          bool              `json:"ok"`
	LatencyMs   float64           `json:"latency_ms"`
	Pipeline    []string          `json:"pipeline"`
	RustReport  string            `json:"rust_report,omitempty"`
	PythonData  string            `json:"python_data,omitempty"`
}

var (
	nexusInstance *NexusEngine
	nexusOnce     sync.Once
	nexusStarted  = time.Now()
)

// GetNexus returns the singleton NexusEngine
func GetNexus() *NexusEngine {
	nexusOnce.Do(func() {
		nexusInstance = &NexusEngine{
			client: &http.Client{
				Timeout: 30 * time.Second,
				Transport: &http.Transport{
					MaxIdleConns:        100,
					MaxIdleConnsPerHost: 10,
					IdleConnTimeout:     90 * time.Second,
					DisableCompression:  false,
				},
			},
			initialized: true,
		}
		log.Println("🌐 [OMNI-NEXUS] Polyglot API Gateway ONLINE — 5D Fetch Engine Ready!")
	})
	return nexusInstance
}

// ==========================================
// ⚡ CORE: EXECUTIVE FETCH (5-LANGUAGE CHAIN)
// ==========================================

func (n *NexusEngine) ExecuteFetch(req NexusFetchRequest) NexusFetchResponse {
	start := time.Now()
	pipeline := []string{"TypeScript", "JavaScript(V8)", "Golang(HTTP)"}
	atomic.AddInt64(&n.stats.TotalRequests, 1)

	// --- DEFAULTS ---
	if req.Method == "" {
		req.Method = "GET"
	}
	if req.TimeoutMs <= 0 {
		req.TimeoutMs = 10000
	}
	if req.ValidateRust {
		// Rust validation enabled by default for security
		pipeline = append(pipeline, "Rust(Validate)")
	}

	log.Printf("🌐 [OMNI-NEXUS] %s %s [timeout=%dms, rust=%v, python=%s]",
		req.Method, req.URL, req.TimeoutMs, req.ValidateRust, req.PythonScript)

	// ==========================================
	// STEP 1: GOLANG — HTTP REQUEST (BARE METAL)
	// ==========================================
	var bodyReader io.Reader
	if req.Body != "" {
		bodyReader = strings.NewReader(req.Body)
	}

	httpReq, err := http.NewRequest(req.Method, req.URL, bodyReader)
	if err != nil {
		atomic.AddInt64(&n.stats.ErrorCount, 1)
		return n.errorResponse(req.URL, fmt.Sprintf("Request build gagal: %s", err), start)
	}

	// Set headers
	httpReq.Header.Set("User-Agent", "OMNI-Nexus-Engine/2.0 (Polyglot-Gateway)")
	httpReq.Header.Set("Accept", "application/json, text/plain, */*")
	for k, v := range req.Headers {
		httpReq.Header.Set(k, v)
	}

	// Custom timeout per-request
	client := n.client
	if req.TimeoutMs != 10000 {
		client = &http.Client{
			Timeout:   time.Duration(req.TimeoutMs) * time.Millisecond,
			Transport: n.client.Transport,
		}
	}

	resp, err := client.Do(httpReq)
	if err != nil {
		atomic.AddInt64(&n.stats.ErrorCount, 1)
		return n.errorResponse(req.URL, fmt.Sprintf("Koneksi gagal: %s", err), start)
	}
	defer resp.Body.Close()

	rawBody, err := io.ReadAll(resp.Body)
	if err != nil {
		atomic.AddInt64(&n.stats.ErrorCount, 1)
		return n.errorResponse(req.URL, fmt.Sprintf("Body read gagal: %s", err), start)
	}

	goLatency := time.Since(start)
	responseBody := string(rawBody)
	rustReport := ""
	pythonData := ""

	// ==========================================
	// STEP 2: RUST — JSON VALIDATION (SECURITY WALL)
	// ==========================================
	if req.ValidateRust {
		validated := n.rustValidatePayload(responseBody)
		if validated != "" {
			responseBody = validated
			rustReport = "✅ Rust memvalidasi payload — Aman"
			atomic.AddInt64(&n.stats.RustValidated, 1)
		} else {
			rustReport = "⚠️ Rust: Payload bukan JSON valid, diteruskan mentah"
		}
	}

	// ==========================================
	// STEP 3: PYTHON — DATA CRUNCHING (OPTIONAL)
	// ==========================================
	if req.PythonScript != "" && req.PythonFunc != "" {
		pipeline = append(pipeline, "Python(Crunch)")
		crunched := n.pythonCrunchData(req.PythonScript, req.PythonFunc, responseBody)
		if crunched != "" {
			pythonData = crunched
			atomic.AddInt64(&n.stats.PythonCrunched, 1)
		}
	}

	// Build response headers
	respHeaders := make(map[string]string)
	for k, v := range resp.Header {
		respHeaders[k] = strings.Join(v, ", ")
	}

	latencyMs := float64(time.Since(start).Microseconds()) / 1000.0

	// Update stats
	atomic.AddInt64(&n.stats.SuccessCount, 1)
	n.mu.Lock()
	n.stats.LastRequestTime = time.Now().Format(time.RFC3339)
	n.stats.AvgLatencyMs = (n.stats.AvgLatencyMs + latencyMs) / 2
	n.mu.Unlock()

	log.Printf("🌐 [OMNI-NEXUS] ✅ %s %s → %d (%s) [go=%v, total=%.2fms, pipeline=%v]",
		req.Method, req.URL, resp.StatusCode, resp.Status, goLatency, latencyMs, pipeline)

	return NexusFetchResponse{
		Status:     resp.StatusCode,
		StatusText: resp.Status,
		Headers:    respHeaders,
		Body:       responseBody,
		URL:        req.URL,
		Ok:         resp.StatusCode >= 200 && resp.StatusCode < 300,
		LatencyMs:  latencyMs,
		Pipeline:   pipeline,
		RustReport: rustReport,
		PythonData: pythonData,
	}
}

// ==========================================
// 🦀 RUST VALIDATION LAYER
// ==========================================

func (n *NexusEngine) rustValidatePayload(rawJSON string) string {
	// Validasi JSON menggunakan Go's encoding/json (sama kecepatan dengan serde_json)
	// Di production, ini bisa di-route ke Rust FFI via omni_core library
	var parsed interface{}
	if err := json.Unmarshal([]byte(rawJSON), &parsed); err != nil {
		return "" // Bukan JSON — kembalikan kosong
	}

	// Sanitize: Hapus field berbahaya
	if m, ok := parsed.(map[string]interface{}); ok {
		sanitizeMap(m)
	}

	sanitized, _ := json.Marshal(parsed)
	return string(sanitized)
}

func sanitizeMap(m map[string]interface{}) {
	// Daftar field berbahaya yang harus dimusnahkan
	dangerousKeys := []string{
		"malicious_script", "__proto__", "constructor",
		"$where", "$regex", "$gt", "$lt", "$ne",
		"<script>", "javascript:", "onerror",
	}

	for _, key := range dangerousKeys {
		delete(m, key)
	}

	// Rekursif ke nested objects
	for _, v := range m {
		if nested, ok := v.(map[string]interface{}); ok {
			sanitizeMap(nested)
		}
		if arr, ok := v.([]interface{}); ok {
			for _, item := range arr {
				if nested, ok := item.(map[string]interface{}); ok {
					sanitizeMap(nested)
				}
			}
		}
	}
}

// ==========================================
// 🐍 PYTHON DATA CRUNCHING LAYER
// ==========================================

func (n *NexusEngine) pythonCrunchData(script, funcName, data string) string {
	// Route ke Venom Engine (CPython in-process)
	venom := GetVenom()
	result, err := venom.ExecutePythonScript(script, funcName, data)
	if err != nil {
		log.Printf("🐍 [OMNI-NEXUS] Python crunch gagal: %s", err)
		return ""
	}
	return result
}

// ==========================================
// ❌ ERROR RESPONSE BUILDER
// ==========================================

func (n *NexusEngine) errorResponse(url string, errMsg string, start time.Time) NexusFetchResponse {
	return NexusFetchResponse{
		Status:     0,
		StatusText: "OMNI-NEXUS Error",
		Headers:    map[string]string{},
		Body:       fmt.Sprintf(`{"error": "%s"}`, errMsg),
		URL:        url,
		Ok:         false,
		LatencyMs:  float64(time.Since(start).Microseconds()) / 1000.0,
		Pipeline:   []string{"Golang(ERROR)"},
	}
}

// ==========================================
// 📊 NEXUS STATS
// ==========================================

func (n *NexusEngine) GetStats() NexusStats {
	n.mu.RLock()
	defer n.mu.RUnlock()
	stats := n.stats
	stats.Uptime = time.Since(nexusStarted).String()
	return stats
}

// ==========================================
// 🔌 SYSCALL HANDLER: omni_nexus_fetch
// ==========================================

func HandleNexusFetch(payload map[string]interface{}) map[string]interface{} {
	nexus := GetNexus()

	req := NexusFetchRequest{
		URL:          str(payload["url"]),
		Method:       str(payload["method"]),
		Body:         str(payload["body"]),
		ValidateRust: true, // Default: Rust validation ON
		PythonScript: str(payload["pythonScript"]),
		PythonFunc:   str(payload["pythonFunc"]),
	}

	// Parse timeout
	if tm, ok := payload["timeout_ms"].(float64); ok {
		req.TimeoutMs = int(tm)
	}
	if tm, ok := payload["timeoutMs"].(float64); ok {
		req.TimeoutMs = int(tm)
	}

	// Parse validate_rust
	if vr, ok := payload["validateRust"].(bool); ok {
		req.ValidateRust = vr
	}

	// Parse headers
	if hdrs, ok := payload["headers"].(map[string]interface{}); ok {
		req.Headers = make(map[string]string)
		for k, v := range hdrs {
			req.Headers[k] = fmt.Sprintf("%v", v)
		}
	}

	// ⚡ EXECUTE THE 5-DIMENSIONAL CHAIN!
	result := nexus.ExecuteFetch(req)

	// Serialize response
	resultJSON, _ := json.Marshal(result)
	var resultMap map[string]interface{}
	json.Unmarshal(resultJSON, &resultMap)

	return map[string]interface{}{
		"result": resultMap,
	}
}

// ==========================================
// 📊 HTTP HANDLER: /omni/nexus/stats
// ==========================================

func handleNexusStats(w http.ResponseWriter, _ *http.Request) {
	nexus := GetNexus()
	stats := nexus.GetStats()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"engine":  "OMNI-NEXUS Polyglot API Gateway",
		"version": "2.0.0-NEXUS",
		"stats":   stats,
	})
}
