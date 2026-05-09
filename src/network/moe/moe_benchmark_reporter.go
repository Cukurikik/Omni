// moe_benchmark_reporter.go — Network Layer: Benchmark Reporter
// Streams SWE-bench and HumanEval performance metrics to centralized telemetry servers.

package network_moe

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type BenchmarkPayload struct {
	ModelID    string  `json:"model_id"`
	Framework  string  `json:"framework"`
	SweScore   float64 `json:"swe_score"`
	HumanScore float64 `json:"human_eval_score"`
	Timestamp  int64   `json:"timestamp"`
}

type TelemetryReporter struct {
	IngestURL  string
	HTTPClient *http.Client
}

func NewTelemetryReporter(url string) *TelemetryReporter {
	return &TelemetryReporter{
		IngestURL: url,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (tr *TelemetryReporter) ReportMetrics(payload BenchmarkPayload) error {
	payload.Timestamp = time.Now().UnixMilli()

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to encode telemetry: %w", err)
	}

	req, err := http.NewRequest("POST", tr.IngestURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := tr.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("network error during telemetry report: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("telemetry rejected with status: %d", resp.StatusCode)
	}

	return nil
}

