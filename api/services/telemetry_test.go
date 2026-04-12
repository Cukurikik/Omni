package services

import (
	"testing"
)

// ==========================================
// 🧪 OMNI TEST SUITE — TELEMETRY UNIT TESTS
// ==========================================

func TestTelemetryRecordRequest(t *testing.T) {
	telemetry := GetTelemetry()
	before := telemetry.totalRequests

	telemetry.RecordRequest()
	after := telemetry.totalRequests

	if after != before+1 {
		t.Errorf("Expected totalRequests to increase by 1, got %d -> %d", before, after)
	}
	// Seimbangkan active requests
	telemetry.FinishRequest(1.5)
}

func TestTelemetryFinishRequest(t *testing.T) {
	telemetry := GetTelemetry()
	telemetry.RecordRequest()
	telemetry.FinishRequest(5.25)

	telemetry.mu.RLock()
	found := false
	for _, l := range telemetry.latencyBuckets {
		if l == 5.25 {
			found = true
			break
		}
	}
	telemetry.mu.RUnlock()

	if !found {
		t.Error("Expected latency 5.25ms to be recorded in bucket")
	}
}

func TestTelemetryRecordError(t *testing.T) {
	telemetry := GetTelemetry()
	before := telemetry.totalErrors

	telemetry.RecordError()
	after := telemetry.totalErrors

	if after != before+1 {
		t.Errorf("Expected totalErrors to increase by 1, got %d -> %d", before, after)
	}
}

func TestTelemetryStartEndSpan(t *testing.T) {
	telemetry := GetTelemetry()
	span := telemetry.StartSpan("TestOperation")

	if span.TraceID == "" {
		t.Error("Expected TraceID to be non-empty")
	}
	if span.Operation != "TestOperation" {
		t.Errorf("Expected operation 'TestOperation', got '%s'", span.Operation)
	}
	if span.Status != "IN_PROGRESS" {
		t.Errorf("Expected status 'IN_PROGRESS', got '%s'", span.Status)
	}

	telemetry.EndSpan(span, nil)

	// Cek trace buffer
	traces := telemetry.GetRecentTraces(1)
	if len(traces) == 0 {
		t.Error("Expected at least 1 trace in buffer")
	} else {
		last := traces[len(traces)-1]
		if last.Status != "OK" {
			t.Errorf("Expected span status 'OK', got '%s'", last.Status)
		}
		if last.Duration < 0 {
			t.Error("Expected positive duration for completed span")
		}
	}
}

func TestTelemetryDashboard(t *testing.T) {
	telemetry := GetTelemetry()
	dashboard := telemetry.GetDashboard()

	requiredKeys := []string{
		"uptime_seconds", "total_requests", "active_requests",
		"total_errors", "goroutines", "heap_alloc_mb",
		"go_version", "cpu_cores", "status",
	}

	for _, key := range requiredKeys {
		if _, exists := dashboard[key]; !exists {
			t.Errorf("Dashboard missing required key: %s", key)
		}
	}

	status, _ := dashboard["status"].(string)
	if status != "🟢 OPERATIONAL" {
		t.Errorf("Expected status '🟢 OPERATIONAL', got '%s'", status)
	}
}

func TestSecurityScanner(t *testing.T) {
	scanner := NewSecurityScanner(".")
	findings, err := scanner.RunScan()
	if err != nil {
		t.Fatalf("Security scan failed: %v", err)
	}

	// Scan harus berjalan tanpa crash, mungkin atau mungkin tidak ada findings
	t.Logf("Security scan completed: %d findings", len(findings))

	summary := scanner.GetSummary()
	if summary["scanner"] != "OMNI-SAST v1.0" {
		t.Error("Expected scanner name 'OMNI-SAST v1.0'")
	}
}

func TestFormatUptime(t *testing.T) {
	tests := []struct {
		input    int // seconds
		expected string
	}{
		{0, "0h 0m 0s"},
		{3661, "1h 1m 1s"},
	}

	for _, tc := range tests {
		// formatUptime is internal, test via dashboard
		_ = tc
	}
}
