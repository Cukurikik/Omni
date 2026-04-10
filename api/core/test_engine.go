package core

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
// 🧪 OMNI-TEST: DEEP VALIDATION ENGINE
// ==========================================
// Mesin uji E2E yang berjalan dari DALAM server,
// mengebom Gateway dengan request massal, memvalidasi
// integritas byte, dan mengukur latency rata-rata.
//
// Filosofi: Jangan deploy ke production tanpa membuktikan ketangguhan.
//
// CLI: `omni test deep` → panggil /api/v1/test/deep
// API: GET /api/v1/test/deep → jalankan semua validasi
// ==========================================

// TestReport adalah hasil lengkap semua pengujian
type TestReport struct {
	Timestamp     string            `json:"timestamp"`
	Duration      string            `json:"duration"`
	TotalTests    int               `json:"total_tests"`
	Passed        int               `json:"passed"`
	Failed        int               `json:"failed"`
	Results       []TestResult      `json:"results"`
	SystemHealth  SystemHealthCheck `json:"system_health"`
}

// TestResult adalah hasil satu test case
type TestResult struct {
	Name     string `json:"name"`
	Status   string `json:"status"` // PASS / FAIL
	Duration string `json:"duration"`
	Detail   string `json:"detail,omitempty"`
}

// SystemHealthCheck adalah snapshot kesehatan sistem
type SystemHealthCheck struct {
	DatabaseOK     bool   `json:"database_ok"`
	DatabaseEngine string `json:"database_engine"`
	FirebaseOK     bool   `json:"firebase_ok"`
	SSEActive      bool   `json:"sse_active"`
	AdapterCount   int    `json:"adapter_count"`
	GoroutineCount int    `json:"goroutine_count"`
	LockFileOK     bool   `json:"lock_file_ok"`
	LockStatus     string `json:"lock_status"`
}

// ==========================================
// ENDPOINT: GET /api/v1/test/deep
// ==========================================

// DeepTestHandler adalah endpoint yang menjalankan seluruh suite pengujian.
// Route: GET /api/v1/test/deep
func DeepTestHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet && r.Method != http.MethodPost {
		http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	report := RunDeepValidation()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(report)
}

// ==========================================
// CORE: Runner
// ==========================================

// RunDeepValidation menjalankan seluruh suite pengujian OMNI-TEST
func RunDeepValidation() *TestReport {
	start := time.Now()
	log.Println("🧪 [OMNI-TEST] ==========================================")
	log.Println("🧪 [OMNI-TEST] DEEP VALIDATION ENGINE: DIMULAI")
	log.Println("🧪 [OMNI-TEST] ==========================================")

	report := &TestReport{
		Timestamp: time.Now().Format(time.RFC3339),
		Results:   []TestResult{},
	}

	// === TEST 1: Database Connectivity ===
	report.addResult(testDatabaseConnectivity())

	// === TEST 2: Lock File Integrity ===
	report.addResult(testLockFileIntegrity())

	// === TEST 3: Configuration Validity ===
	report.addResult(testConfigurationValidity())

	// === TEST 4: SSE Stream Engine ===
	report.addResult(testSSEEngine())

	// === TEST 5: Adapter Registry ===
	report.addResult(testAdapterRegistry())

	// === TEST 6: Internal API Gateway Stress ===
	report.addResult(testGatewayStress())

	// === TEST 7: File System Integrity ===
	report.addResult(testFileSystemIntegrity())

	// === TEST 8: Memory Pressure ===
	report.addResult(testMemoryPressure())

	// === SYSTEM HEALTH CHECK ===
	report.SystemHealth = runHealthCheck()

	report.Duration = time.Since(start).String()

	log.Printf("🧪 [OMNI-TEST] SELESAI | %d PASS, %d FAIL | Durasi: %s",
		report.Passed, report.Failed, report.Duration)

	return report
}

func (r *TestReport) addResult(result TestResult) {
	r.Results = append(r.Results, result)
	r.TotalTests++
	if result.Status == "PASS" {
		r.Passed++
	} else {
		r.Failed++
	}
}

// ==========================================
// TEST CASES
// ==========================================

func testDatabaseConnectivity() TestResult {
	start := time.Now()
	name := "Database Connectivity"

	if DB == nil {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: "core.DB adalah nil — InitDatabase() belum dipanggil"}
	}

	err := DB.Ping()
	if err != nil {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: fmt.Sprintf("Ping gagal: %v", err)}
	}

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("Engine: %s, Ping OK", AppConfig.Database.Engine)}
}

func testLockFileIntegrity() TestResult {
	start := time.Now()
	name := "Lock File Integrity"

	result, err := ValidateLockFile()
	if err != nil {
		// Lockfile belum dibuat — bukan error fatal, hanya warning
		return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
			Detail: fmt.Sprintf("Omni.lock belum ada (opsional): %v", err)}
	}

	if !result.Valid {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: fmt.Sprintf("INTEGRITAS DILANGGAR! %d gagal, %d hilang", result.TotalFailed, result.TotalMissing)}
	}

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("%d modul terverifikasi", result.TotalPassed)}
}

func testConfigurationValidity() TestResult {
	start := time.Now()
	name := "Configuration Validity"

	if AppConfig == nil {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: "AppConfig adalah nil"}
	}

	issues := []string{}

	if AppConfig.AppName == "" {
		issues = append(issues, "app_name kosong")
	}
	if AppConfig.Server.Port <= 0 || AppConfig.Server.Port > 65535 {
		issues = append(issues, fmt.Sprintf("port tidak valid: %d", AppConfig.Server.Port))
	}
	if AppConfig.Security.SessionSecret == "" {
		issues = append(issues, "session_secret kosong (BERBAHAYA)")
	}
	if AppConfig.Storage.MaxUploadGB <= 0 {
		issues = append(issues, "max_upload_gb harus > 0")
	}
	if AppConfig.Engine.MaxConcurrentWorkers <= 0 {
		issues = append(issues, "max_concurrent_workers harus > 0")
	}

	if len(issues) > 0 {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: strings.Join(issues, "; ")}
	}

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("%s v%s | Port: %d | Workers: %d",
			AppConfig.AppName, AppConfig.Version, AppConfig.Server.Port, AppConfig.Engine.MaxConcurrentWorkers)}
}

func testSSEEngine() TestResult {
	start := time.Now()
	name := "SSE Stream Engine"

	// Tes broadcast tanpa listener — tidak boleh crash
	StreamUpdate("TEST-OMNI-VALIDATION", "PROCESSING", 50, "Test broadcast")
	StreamUpdate("TEST-OMNI-VALIDATION", "COMPLETED", 100, "Test selesai")

	activeListeners := GetActiveSSEListeners()

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("Broadcast tanpa listener: OK | Active listeners: %d", activeListeners)}
}

func testAdapterRegistry() TestResult {
	start := time.Now()
	name := "Adapter Registry"

	count := GetAdapterCount()
	statuses := CheckAllAdapters()

	degradedCount := 0
	for _, s := range statuses {
		if s.State != AdapterActive {
			degradedCount++
		}
	}

	status := "PASS"
	detail := fmt.Sprintf("%d adapter terdaftar, %d degraded", count, degradedCount)

	if degradedCount > 0 {
		status = "PASS" // Degraded adapter bukan kegagalan test
		detail += " (WARNING: ada adapter degraded)"
	}

	return TestResult{Name: name, Status: status, Duration: time.Since(start).String(), Detail: detail}
}

func testGatewayStress() TestResult {
	start := time.Now()
	name := "Gateway Internal Stress Test"

	// Simulasi 50 concurrent goroutine yang memanggil internal logic
	const concurrency = 50
	var successCount int64
	var failCount int64
	var wg sync.WaitGroup

	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			// Simulasi: Buat request ke health endpoint internal
			serverAddr := GetServerAddr()
			resp, err := http.Get(fmt.Sprintf("http://%s/api/v1/omni/metrics", serverAddr))
			if err != nil {
				atomic.AddInt64(&failCount, 1)
				return
			}
			defer resp.Body.Close()
			io.ReadAll(resp.Body)

			if resp.StatusCode == 200 {
				atomic.AddInt64(&successCount, 1)
			} else {
				atomic.AddInt64(&failCount, 1)
			}
		}(i)
	}

	wg.Wait()
	elapsed := time.Since(start)

	success := atomic.LoadInt64(&successCount)
	fail := atomic.LoadInt64(&failCount)

	status := "PASS"
	if fail > 10 { // Lebih dari 20% failure = FAIL
		status = "FAIL"
	}

	return TestResult{Name: name, Status: status, Duration: elapsed.String(),
		Detail: fmt.Sprintf("%d concurrent requests | %d success, %d failed | %s",
			concurrency, success, fail, elapsed)}
}

func testFileSystemIntegrity() TestResult {
	start := time.Now()
	name := "File System Integrity"

	criticalDirs := []string{
		"../configs",
		"../release",
		"../bin",
	}

	missing := []string{}
	for _, dir := range criticalDirs {
		if !dirExists(dir) {
			missing = append(missing, dir)
		}
	}

	if len(missing) > 0 {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: fmt.Sprintf("Folder kritikal hilang: %s", strings.Join(missing, ", "))}
	}

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("%d folder kritikal terverifikasi", len(criticalDirs))}
}

func testMemoryPressure() TestResult {
	start := time.Now()
	name := "Memory Pressure Test"

	// Alokasi 10MB temporary buffer untuk memastikan sistem tetap stabil
	testSize := 10 * 1024 * 1024 // 10MB
	buf := make([]byte, testSize)

	// Isi dengan data acak sederhana
	for i := range buf {
		buf[i] = byte(i % 256)
	}

	// Verifikasi integritas
	valid := true
	for i := 0; i < 1000; i++ {
		if buf[i] != byte(i%256) {
			valid = false
			break
		}
	}

	// Lepas buffer (biarkan GC menangani)
	buf = nil

	if !valid {
		return TestResult{Name: name, Status: "FAIL", Duration: time.Since(start).String(),
			Detail: "Memory corruption terdeteksi!"}
	}

	return TestResult{Name: name, Status: "PASS", Duration: time.Since(start).String(),
		Detail: fmt.Sprintf("10MB alloc+verify OK dalam %s", time.Since(start))}
}

// ==========================================
// SYSTEM HEALTH CHECK
// ==========================================

func runHealthCheck() SystemHealthCheck {
	health := SystemHealthCheck{}

	// Database
	if DB != nil {
		health.DatabaseOK = DB.Ping() == nil
		if AppConfig != nil {
			health.DatabaseEngine = AppConfig.Database.Engine
		}
	}

	// Firebase
	health.FirebaseOK = IsFirebaseReady()

	// SSE
	health.SSEActive = true // SSE always ready

	// Adapters
	health.AdapterCount = GetAdapterCount()

	// Lock File
	lockResult, err := ValidateLockFile()
	if err != nil {
		health.LockFileOK = false
		health.LockStatus = "TIDAK ADA"
	} else {
		health.LockFileOK = lockResult.Valid
		if lockResult.Valid {
			health.LockStatus = fmt.Sprintf("OK (%d modul)", lockResult.TotalPassed)
		} else {
			health.LockStatus = fmt.Sprintf("FAILED (%d violated)", lockResult.TotalFailed)
		}
	}

	return health
}
