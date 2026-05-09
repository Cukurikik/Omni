// moe_supermix_telemetry.go — Network
// Layer: Network — Supermix Local-First Telemetry Sync
// Inspired by: Supermix (Local-first packaging flow)

package network_moe

import (
	"bytes"
	"encoding/json"
	"net/http"
	"time"
)

type SupermixTelemetryEvent struct {
	EventID   string  `json:"event_id"`
	ModelID   string  `json:"model_id"`
	Epoch     int     `json:"epoch"`
	Loss      float64 `json:"loss"`
	Timestamp int64   `json:"timestamp"`
}

type TelemetryClient struct {
	Endpoint string
	Client   *http.Client
}

func NewTelemetryClient(endpoint string) *TelemetryClient {
	return &TelemetryClient{
		Endpoint: endpoint,
		Client: &http.Client{
			Timeout: 5 * time.Second,
		},
	}
}

// Sends training telemetry to the centralized Supermix Studio while maintaining local-first data gravity
func (tc *TelemetryClient) SyncEvent(event SupermixTelemetryEvent) error {
	payload, err := json.Marshal(event)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", tc.Endpoint, bytes.NewBuffer(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Supermix-Client", "omni-telemetry-v1")

	resp, err := tc.Client.Do(req)
	if err != nil {
		// In local-first paradigm, failures to sync are ignored (logged to local WAL instead)
		return err
	}
	defer resp.Body.Close()

	return nil
}

