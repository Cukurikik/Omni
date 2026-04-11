package cloud

import (
	"context"
	"os/exec"
	"strings"
	"testing"
	"time"
)

// ==========================================
// 🧪 OMNI CLI PASSTHROUGH — TEST SUITE
// ==========================================
// Verifikasi bahwa router OMNI CLI dapat menemukan dan
// memanggil binary GCP di lingkungan host OS.
// ==========================================

const testProjectID = "omni-tool-9c48b"

// TestNewCLIPassthrough memverifikasi konstruksi router
func TestNewCLIPassthrough(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 30*time.Second)

	if router == nil {
		t.Fatal("NewCLIPassthrough mengembalikan nil — konstruksi gagal")
	}
	if router.projectID != testProjectID {
		t.Errorf("ProjectID mismatch: got %q, want %q", router.projectID, testProjectID)
	}
	if router.timeout != 30*time.Second {
		t.Errorf("Timeout mismatch: got %v, want %v", router.timeout, 30*time.Second)
	}
	if router.binaryCache == nil {
		t.Fatal("Binary cache tidak diinisialisasi")
	}

	t.Log("✅ [PASS] CLIPassthroughRouter berhasil dikonstruksi")
}

// TestDefaultTimeout memverifikasi timeout default 5 menit
func TestDefaultTimeout(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 0)

	if router.timeout != 5*time.Minute {
		t.Errorf("Default timeout seharusnya 5m, got: %v", router.timeout)
	}
	t.Log("✅ [PASS] Default timeout 5 menit terverifikasi")
}

// TestResolveBinaryGcloud mencari binary gcloud di sistem
func TestResolveBinaryGcloud(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 10*time.Second)

	path, err := router.resolveBinary("gcloud")
	if err != nil {
		// Ini bukan failure fatal — bisa jadi GCloud belum terinstall di dev PC
		cliErr, ok := err.(*CLIError)
		if ok && cliErr.Code == ErrBinaryNotFound {
			t.Skipf("⚠️  [SKIP] gcloud belum terinstall di sistem ini: %s", cliErr.Message)
		}
		t.Fatalf("Unexpected error: %v", err)
	}

	if path == "" {
		t.Fatal("Binary path kosong padahal tidak ada error")
	}

	t.Logf("✅ [PASS] gcloud ditemukan di: %s", path)
}

// TestResolveBinaryBQ mencari binary bq di sistem
func TestResolveBinaryBQ(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 10*time.Second)

	path, err := router.resolveBinary("bq")
	if err != nil {
		cliErr, ok := err.(*CLIError)
		if ok && cliErr.Code == ErrBinaryNotFound {
			t.Skipf("⚠️  [SKIP] bq belum terinstall di sistem ini: %s", cliErr.Message)
		}
		t.Fatalf("Unexpected error: %v", err)
	}

	t.Logf("✅ [PASS] bq ditemukan di: %s", path)
}

// TestResolveBinaryFirebase mencari binary firebase di sistem
func TestResolveBinaryFirebase(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 10*time.Second)

	path, err := router.resolveBinary("firebase")
	if err != nil {
		cliErr, ok := err.(*CLIError)
		if ok && cliErr.Code == ErrBinaryNotFound {
			t.Skipf("⚠️  [SKIP] firebase belum terinstall di sistem ini: %s", cliErr.Message)
		}
		t.Fatalf("Unexpected error: %v", err)
	}

	t.Logf("✅ [PASS] firebase ditemukan di: %s", path)
}

// TestBinaryCaching memverifikasi bahwa binary path di-cache setelah resolve pertama
func TestBinaryCaching(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 10*time.Second)

	// Cari binary yang pasti ada di semua sistem
	testBinary := "go"
	path1, err := router.resolveBinary(testBinary)
	if err != nil {
		t.Skipf("⚠️  [SKIP] '%s' tidak tersedia: %v", testBinary, err)
	}

	// Cache harus terisi setelah resolve pertama
	router.mu.RLock()
	cachedPath, exists := router.binaryCache[testBinary]
	router.mu.RUnlock()

	if !exists {
		t.Fatal("Binary cache TIDAK terisi setelah resolve pertama — pelanggaran performa!")
	}
	if cachedPath != path1 {
		t.Errorf("Cached path mismatch: %q vs %q", cachedPath, path1)
	}

	// Resolve kedua harus gunakan cache (lebih cepat)
	path2, _ := router.resolveBinary(testBinary)
	if path1 != path2 {
		t.Errorf("Resolve kedua mengembalikan path berbeda: %q vs %q", path1, path2)
	}

	t.Logf("✅ [PASS] Binary caching berfungsi sempurna untuk '%s'", testBinary)
}

// TestResolveBinaryNotFound memverifikasi error monadic untuk binary tidak ditemukan
func TestResolveBinaryNotFound(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 10*time.Second)

	_, err := router.resolveBinary("omni_nonexistent_phantom_binary_xyz")
	if err == nil {
		t.Fatal("Seharusnya mengembalikan error untuk binary yang tidak ada!")
	}

	cliErr, ok := err.(*CLIError)
	if !ok {
		t.Fatalf("Error bukan tipe *CLIError: %T", err)
	}

	if cliErr.Code != ErrBinaryNotFound {
		t.Errorf("Error code salah: got %q, want %q", cliErr.Code, ErrBinaryNotFound)
	}

	if !strings.Contains(cliErr.Message, "tidak ditemukan") {
		t.Errorf("Pesan error kurang informatif: %s", cliErr.Message)
	}

	t.Logf("✅ [PASS] Monadic error handling berfungsi: %s", cliErr.Error())
}

// TestExecuteGcloudInfo menjalankan `gcloud info` melalui OMNI CLI
// Ini adalah Sanity Check utama — memverifikasi bahwa OMNI CLI
// mampu memanggil gcloud secara transparan
func TestExecuteGcloudInfo(t *testing.T) {
	// Cek dulu apakah gcloud tersedia
	if _, err := exec.LookPath("gcloud"); err != nil {
		t.Skip("⚠️  [SKIP] gcloud tidak tersedia di sistem ini")
	}

	router := NewCLIPassthrough(testProjectID, 30*time.Second)
	ctx := context.Background()

	result, err := router.ExecuteGcloud(ctx, "info", "--format=value(config.project)")
	if err != nil {
		t.Fatalf("ExecuteGcloud gagal: %v", err)
	}

	if result.ExitCode != 0 {
		t.Errorf("gcloud info exit code: %d (expected 0). Stderr: %s",
			result.ExitCode, result.Stderr)
	}

	if result.Duration <= 0 {
		t.Error("Duration harus positif")
	}

	t.Logf("✅ [PASS] gcloud info berhasil via OMNI CLI (took: %v)", result.Duration)
	t.Logf("   Project aktif: %s", strings.TrimSpace(result.Stdout))
}

// TestExecuteBQVersion menjalankan `bq version` melalui OMNI CLI
func TestExecuteBQVersion(t *testing.T) {
	if _, err := exec.LookPath("bq"); err != nil {
		t.Skip("⚠️  [SKIP] bq tidak tersedia di sistem ini")
	}

	router := NewCLIPassthrough(testProjectID, 30*time.Second)
	ctx := context.Background()

	result, err := router.ExecuteBQ(ctx, "version")
	if err != nil {
		t.Fatalf("ExecuteBQ gagal: %v", err)
	}

	if result.ExitCode != 0 {
		t.Errorf("bq version exit code: %d. Stderr: %s", result.ExitCode, result.Stderr)
	}

	t.Logf("✅ [PASS] bq version berhasil via OMNI CLI: %s",
		strings.TrimSpace(result.Stdout))
}

// TestExecuteFirebaseVersion menjalankan `firebase --version` melalui OMNI CLI
func TestExecuteFirebaseVersion(t *testing.T) {
	// Firebase bisa berupa firebase.cmd di Windows
	found := false
	for _, name := range []string{"firebase", "firebase.cmd"} {
		if _, err := exec.LookPath(name); err == nil {
			found = true
			break
		}
	}
	if !found {
		t.Skip("⚠️  [SKIP] firebase tidak tersedia di sistem ini")
	}

	router := NewCLIPassthrough(testProjectID, 30*time.Second)
	ctx := context.Background()

	result, err := router.ExecuteFirebase(ctx, "--version")
	if err != nil {
		t.Fatalf("ExecuteFirebase gagal: %v", err)
	}

	if result.ExitCode != 0 {
		t.Errorf("firebase --version exit code: %d. Stderr: %s",
			result.ExitCode, result.Stderr)
	}

	t.Logf("✅ [PASS] firebase version berhasil via OMNI CLI: %s",
		strings.TrimSpace(result.Stdout))
}

// TestVerifyADC memverifikasi Application Default Credentials
func TestVerifyADC(t *testing.T) {
	if _, err := exec.LookPath("gcloud"); err != nil {
		t.Skip("⚠️  [SKIP] gcloud tidak tersedia — ADC check dilewati")
	}

	router := NewCLIPassthrough(testProjectID, 15*time.Second)
	ctx := context.Background()

	result, err := router.VerifyADC(ctx)
	if err != nil {
		cliErr, ok := err.(*CLIError)
		if ok && cliErr.Code == ErrADCMissing {
			t.Logf("⚠️  [WARN] ADC belum dikonfigurasi (ini normal di dev lokal): %s", cliErr.Message)
			t.Skip("ADC belum dikonfigurasi — jalankan `gcloud auth application-default login`")
		}
		t.Fatalf("VerifyADC error tak terduga: %v", err)
	}

	if result.ExitCode != 0 {
		t.Skipf("⚠️  ADC gagal (exit %d) — kemungkinan belum login", result.ExitCode)
	}

	// Token seharusnya dimulai dengan "ya29." (Google OAuth2 access token format)
	token := strings.TrimSpace(result.Stdout)
	if len(token) > 10 {
		t.Logf("✅ [PASS] ADC terverifikasi! Token prefix: %s...", token[:10])
	} else {
		t.Logf("✅ [PASS] ADC merespons (output length: %d)", len(token))
	}
}

// TestSanityCheck menjalankan diagnostik penuh
func TestSanityCheck(t *testing.T) {
	router := NewCLIPassthrough(testProjectID, 30*time.Second)
	ctx := context.Background()

	report, err := router.SanityCheck(ctx)
	if err != nil {
		t.Fatalf("SanityCheck gagal: %v", err)
	}

	if report == nil {
		t.Fatal("SanityReport nil")
	}

	if report.Timestamp.IsZero() {
		t.Error("Timestamp kosong")
	}

	if report.ProjectID != testProjectID {
		t.Errorf("ProjectID mismatch: %q vs %q", report.ProjectID, testProjectID)
	}

	// Hitung berapa tools yang tersedia
	available := 0
	for name, status := range report.Tools {
		if status.Available {
			available++
			t.Logf("   ✅ %s: %s", name, status.Version)
		} else {
			t.Logf("   ⚠️  %s: NOT AVAILABLE (%s)", name, status.Error)
		}
	}

	t.Logf("✅ [PASS] Sanity Check selesai — %d/%d tools tersedia, ADC: %v",
		available, len(report.Tools), report.ADCConfigured)
}

// TestCLIErrorInterface memverifikasi implementasi error interface
func TestCLIErrorInterface(t *testing.T) {
	cliErr := &CLIError{
		Tool:    "gcloud",
		Message: "Binary tidak ditemukan",
		Code:    ErrBinaryNotFound,
	}

	// Pastikan implements error interface
	var err error = cliErr
	errStr := err.Error()

	if !strings.Contains(errStr, "OMNI_CLI_ERROR") {
		t.Errorf("Error string tidak mengandung prefix OMNI: %s", errStr)
	}
	if !strings.Contains(errStr, ErrBinaryNotFound) {
		t.Errorf("Error string tidak mengandung error code: %s", errStr)
	}
	if !strings.Contains(errStr, "gcloud") {
		t.Errorf("Error string tidak menyebut tool name: %s", errStr)
	}

	t.Logf("✅ [PASS] CLIError interface: %s", errStr)
}
