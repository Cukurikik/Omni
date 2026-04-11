package cloud

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"sync"
	"time"
)

// ==========================================
// ⚡ OMNI CLI PASSTHROUGH ROUTER
// ==========================================
// Membungkus eksekusi `gcloud`, `bq`, dan `firebase` CLI
// dalam arsitektur OMNI TTY streaming zero-buffer.
//
// Developer OMNI cukup menjalankan:
//   omni gcloud compute instances list
//   omni bq query --use_legacy_sql=false "SELECT ..."
//   omni firebase deploy --only functions
//
// dan perintah tersebut diteruskan secara transparan ke
// binary GCP asli yang sudah terinstall di host OS.
// ==========================================

// CLIResult menggunakan pola Monadic Result (OMNI Strict Rule 3.1)
type CLIResult struct {
	ExitCode   int           `json:"exit_code"`
	Stdout     string        `json:"stdout"`
	Stderr     string        `json:"stderr"`
	Duration   time.Duration `json:"duration"`
	BinaryPath string        `json:"binary_path"`
	Command    string        `json:"command"`
}

// CLIError implementasi error monadic untuk CLI passthrough
type CLIError struct {
	Tool    string `json:"tool"`
	Message string `json:"message"`
	Code    string `json:"code"`
}

func (e *CLIError) Error() string {
	return fmt.Sprintf("OMNI_CLI_ERROR [%s] %s: %s", e.Code, e.Tool, e.Message)
}

// Kode error OMNI CLI
const (
	ErrBinaryNotFound  = "E_CLI_001"
	ErrExecutionFailed = "E_CLI_002"
	ErrADCMissing      = "E_CLI_003"
	ErrTimeout         = "E_CLI_004"
	ErrPermission      = "E_CLI_005"
)

// CLIPassthroughRouter adalah inti multiplexer CLI OMNI ke GCP
type CLIPassthroughRouter struct {
	// mu melindungi concurrent access ke binary cache
	mu          sync.RWMutex
	binaryCache map[string]string
	projectID   string
	timeout     time.Duration
}

// NewCLIPassthrough membuat instance router baru
func NewCLIPassthrough(projectID string, timeout time.Duration) *CLIPassthroughRouter {
	if timeout == 0 {
		timeout = 5 * time.Minute // default 5 menit untuk operasi GCP
	}
	return &CLIPassthroughRouter{
		binaryCache: make(map[string]string),
		projectID:   projectID,
		timeout:     timeout,
	}
}

// ============================================
// 🧠 Core Engine: Zero-Buffer TTY Streaming
// ============================================

// executeWithStreaming menjalankan command GCP dengan TTY passthrough langsung.
// Output di-stream REAL-TIME ke stdout/stderr OMNI tanpa buffering.
// Ini memberi ilusi bahwa developer mengetik langsung di terminal GCP.
func (r *CLIPassthroughRouter) executeWithStreaming(ctx context.Context, binaryName string, args []string) (*CLIResult, error) {
	// 1. Resolve binary path (cached)
	binaryPath, err := r.resolveBinary(binaryName)
	if err != nil {
		return nil, err
	}

	// 2. Build command dengan context timeout
	cmdCtx, cancel := context.WithTimeout(ctx, r.timeout)
	defer cancel()

	fullArgs := args
	cmd := exec.CommandContext(cmdCtx, binaryPath, fullArgs...)

	// 3. Capture output untuk Result sementara stream ke terminal
	var stdoutBuf, stderrBuf bytes.Buffer

	// Multiplexer: tulis ke buffer DAN ke os.Stdout/os.Stderr secara bersamaan
	// Ini memberikan zero-buffer TTY streaming (developer melihat output real-time)
	// DAN menyimpan output untuk CLIResult (untuk logging/processing)
	cmd.Stdout = io.MultiWriter(os.Stdout, &stdoutBuf)
	cmd.Stderr = io.MultiWriter(os.Stderr, &stderrBuf)
	cmd.Stdin = os.Stdin // Passthrough input (untuk gcloud auth login, etc.)

	// 4. Environment variables
	cmd.Env = append(os.Environ(),
		fmt.Sprintf("CLOUDSDK_CORE_PROJECT=%s", r.projectID),
		"CLOUDSDK_CORE_DISABLE_PROMPTS=0", // Izinkan prompt interaktif
	)

	commandStr := fmt.Sprintf("%s %s", binaryName, strings.Join(args, " "))
	log.Printf("⚡ [OMNI CLI] Executing: %s", commandStr)
	startTime := time.Now()

	// 5. Execute — Zero-Buffer (output langsung ke terminal)
	runErr := cmd.Run()
	elapsed := time.Since(startTime)

	result := &CLIResult{
		ExitCode:   0,
		Stdout:     stdoutBuf.String(),
		Stderr:     stderrBuf.String(),
		Duration:   elapsed,
		BinaryPath: binaryPath,
		Command:    commandStr,
	}

	if runErr != nil {
		if exitErr, ok := runErr.(*exec.ExitError); ok {
			result.ExitCode = exitErr.ExitCode()
		} else if cmdCtx.Err() == context.DeadlineExceeded {
			return result, &CLIError{
				Tool:    binaryName,
				Message: fmt.Sprintf("Command exceeded timeout of %v", r.timeout),
				Code:    ErrTimeout,
			}
		} else {
			return result, &CLIError{
				Tool:    binaryName,
				Message: runErr.Error(),
				Code:    ErrExecutionFailed,
			}
		}
	}

	log.Printf("✅ [OMNI CLI] Completed in %v (exit: %d)", elapsed, result.ExitCode)
	return result, nil
}

// resolveBinary mencari lokasi binary di PATH OS (dengan caching)
func (r *CLIPassthroughRouter) resolveBinary(name string) (string, error) {
	// Check cache first
	r.mu.RLock()
	if cached, ok := r.binaryCache[name]; ok {
		r.mu.RUnlock()
		return cached, nil
	}
	r.mu.RUnlock()

	// Untuk Windows, cari versi .cmd juga
	candidates := []string{name}
	if runtime.GOOS == "windows" {
		candidates = append(candidates, name+".cmd", name+".bat", name+".exe")
	}

	for _, candidate := range candidates {
		path, err := exec.LookPath(candidate)
		if err == nil {
			// Cache untuk reuse
			r.mu.Lock()
			r.binaryCache[name] = path
			r.mu.Unlock()
			log.Printf("🔍 [OMNI CLI] Resolved '%s' → %s", name, path)
			return path, nil
		}
	}

	return "", &CLIError{
		Tool: name,
		Message: fmt.Sprintf(
			"Binary '%s' tidak ditemukan di PATH sistem. "+
				"Pastikan Google Cloud SDK sudah terinstall: https://cloud.google.com/sdk/docs/install", name),
		Code: ErrBinaryNotFound,
	}
}

// ============================================
// 🌩️ ExecuteGcloud — Google Cloud CLI Router
// ============================================
// Meneruskan perintah `gcloud` secara transparan.
//
// Contoh:
//
//	router.ExecuteGcloud(ctx, "compute", "instances", "list")
//	router.ExecuteGcloud(ctx, "run", "deploy", "omni-api", "--region", "asia-southeast2")
//	router.ExecuteGcloud(ctx, "auth", "application-default", "login")
func (r *CLIPassthroughRouter) ExecuteGcloud(ctx context.Context, args ...string) (*CLIResult, error) {
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	log.Println("☁️  OMNI CLI → Google Cloud SDK (gcloud)")
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	return r.executeWithStreaming(ctx, "gcloud", args)
}

// ============================================
// 📊 ExecuteBQ — BigQuery CLI Router
// ============================================
// Meneruskan perintah `bq` untuk operasi BigQuery.
//
// Contoh:
//
//	router.ExecuteBQ(ctx, "query", "--use_legacy_sql=false", "SELECT * FROM `omni_telemetry_live.logs` LIMIT 10")
//	router.ExecuteBQ(ctx, "ls", "--project_id=omni-tool-9c48b")
//	router.ExecuteBQ(ctx, "show", "omni_telemetry_live")
func (r *CLIPassthroughRouter) ExecuteBQ(ctx context.Context, args ...string) (*CLIResult, error) {
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	log.Println("📊 OMNI CLI → BigQuery CLI (bq)")
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	// Inject project ID otomatis jika belum ada
	hasProject := false
	for _, arg := range args {
		if strings.HasPrefix(arg, "--project_id") || strings.HasPrefix(arg, "--project") {
			hasProject = true
			break
		}
	}
	if !hasProject && r.projectID != "" {
		args = append(args, fmt.Sprintf("--project_id=%s", r.projectID))
	}

	return r.executeWithStreaming(ctx, "bq", args)
}

// ============================================
// 🔥 ExecuteFirebase — Firebase CLI Router
// ============================================
// Meneruskan perintah `firebase` untuk operasi Firebase.
//
// Contoh:
//
//	router.ExecuteFirebase(ctx, "deploy", "--only", "functions")
//	router.ExecuteFirebase(ctx, "emulators:start")
//	router.ExecuteFirebase(ctx, "hosting:channel:deploy", "preview")
func (r *CLIPassthroughRouter) ExecuteFirebase(ctx context.Context, args ...string) (*CLIResult, error) {
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	log.Println("🔥 OMNI CLI → Firebase CLI (firebase)")
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	// Inject --project otomatis jika belum ada
	hasProject := false
	for _, arg := range args {
		if arg == "--project" || strings.HasPrefix(arg, "--project=") {
			hasProject = true
			break
		}
	}
	if !hasProject && r.projectID != "" {
		args = append(args, "--project", r.projectID)
	}

	return r.executeWithStreaming(ctx, "firebase", args)
}

// ============================================
// 🔐 VerifyADC — Application Default Credentials Check
// ============================================
// Memverifikasi bahwa ADC tersedia untuk otorisasi GCP API.
// Ini dipanggil sebelum eksekusi API native (Cloud Storage, Pub/Sub, dll.)
func (r *CLIPassthroughRouter) VerifyADC(ctx context.Context) (*CLIResult, error) {
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	log.Println("🔐 OMNI CLI → ADC (Application Default Credentials) Check")
	log.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	result, err := r.executeWithStreaming(ctx, "gcloud", []string{
		"auth", "application-default", "print-access-token",
	})
	if err != nil {
		return result, &CLIError{
			Tool: "gcloud",
			Message: "Application Default Credentials belum dikonfigurasi. " +
				"Jalankan: omni gcloud auth application-default login",
			Code: ErrADCMissing,
		}
	}

	if result.ExitCode != 0 {
		return result, &CLIError{
			Tool: "gcloud",
			Message: fmt.Sprintf(
				"ADC verification failed (exit %d). Stderr: %s",
				result.ExitCode, strings.TrimSpace(result.Stderr)),
			Code: ErrADCMissing,
		}
	}

	log.Println("✅ [OMNI CLI] ADC terverifikasi — kredensial Google Cloud aktif!")
	return result, nil
}

// ============================================
// 🧪 SanityCheck — Full System Diagnostic
// ============================================
// Menjalankan diagnostik lengkap terhadap semua binary GCP
// yang tersedia di lingkungan OMNI.
//
// Output identik dengan menjalankan:
//
//	gcloud info
//	bq version
//	firebase --version
func (r *CLIPassthroughRouter) SanityCheck(ctx context.Context) (*SanityReport, error) {
	log.Println("=========================================")
	log.Println("🧪 OMNI CLI SANITY CHECK — DIAGNOSTIK PENUH")
	log.Println("=========================================")

	report := &SanityReport{
		Timestamp: time.Now(),
		Tools:     make(map[string]*ToolStatus),
	}

	// 1. gcloud info
	gcloudResult, gcloudErr := r.executeWithStreaming(ctx, "gcloud", []string{"info", "--format=json"})
	report.Tools["gcloud"] = &ToolStatus{
		Available: gcloudErr == nil && gcloudResult.ExitCode == 0,
		Version:   extractVersion(gcloudResult),
		Error:     errorToString(gcloudErr),
	}

	// 2. bq version
	bqResult, bqErr := r.executeWithStreaming(ctx, "bq", []string{"version"})
	report.Tools["bq"] = &ToolStatus{
		Available: bqErr == nil && bqResult.ExitCode == 0,
		Version:   extractVersion(bqResult),
		Error:     errorToString(bqErr),
	}

	// 3. firebase --version
	fbResult, fbErr := r.executeWithStreaming(ctx, "firebase", []string{"--version"})
	report.Tools["firebase"] = &ToolStatus{
		Available: fbErr == nil && fbResult.ExitCode == 0,
		Version:   extractVersion(fbResult),
		Error:     errorToString(fbErr),
	}

	// 4. ADC Check (silent — tanpa streaming ke TTY)
	adcAvailable := false
	adcPath := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
	if adcPath != "" {
		if _, err := os.Stat(adcPath); err == nil {
			adcAvailable = true
		}
	}
	// Juga cek default location
	if !adcAvailable {
		homeDir, _ := os.UserHomeDir()
		defaultADC := fmt.Sprintf("%s/.config/gcloud/application_default_credentials.json", homeDir)
		if _, err := os.Stat(defaultADC); err == nil {
			adcAvailable = true
			adcPath = defaultADC
		}
	}
	report.ADCConfigured = adcAvailable
	report.ADCPath = adcPath
	report.ProjectID = r.projectID

	// Summary
	availableCount := 0
	for _, status := range report.Tools {
		if status.Available {
			availableCount++
		}
	}

	log.Println("=========================================")
	log.Printf("📊 OMNI CLI SANITY REPORT")
	log.Printf("   Tools Available : %d / %d", availableCount, len(report.Tools))
	log.Printf("   ADC Configured  : %v", adcAvailable)
	log.Printf("   GCP Project     : %s", r.projectID)
	log.Println("=========================================")

	return report, nil
}

// SanityReport berisi hasil diagnostik seluruh binary GCP
type SanityReport struct {
	Timestamp     time.Time              `json:"timestamp"`
	Tools         map[string]*ToolStatus `json:"tools"`
	ADCConfigured bool                   `json:"adc_configured"`
	ADCPath       string                 `json:"adc_path"`
	ProjectID     string                 `json:"project_id"`
}

// ToolStatus menyimpan status individual setiap tool
type ToolStatus struct {
	Available bool   `json:"available"`
	Version   string `json:"version"`
	Error     string `json:"error,omitempty"`
}

// extractVersion mengambil versi dari output CLI
func extractVersion(result *CLIResult) string {
	if result == nil {
		return "N/A"
	}
	output := strings.TrimSpace(result.Stdout)
	if output == "" {
		return "N/A"
	}
	// Ambil baris pertama sebagai representasi versi
	lines := strings.Split(output, "\n")
	if len(lines) > 0 {
		return strings.TrimSpace(lines[0])
	}
	return output
}

// errorToString konversi error ke string (monadic nil-safe)
func errorToString(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}
