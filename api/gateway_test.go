package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"omnitools/telepathy"
)

// ==========================================
// 🧪 OMNI GATEWAY INTEGRATION TEST (Wave 23)
// ==========================================
// Tests the full HTTP round-trip of the Telepathy Gateway:
// POST /invoke → JSON Decode → TelepathyRouter → JSON Response

// Helper to invoke a telepathy method via HTTP
func invokeTelepathy(t *testing.T, method string, args map[string]interface{}) *httptest.ResponseRecorder {
	t.Helper()
	reqBody := telepathy.OmniRequest{
		Method: method,
		Args:   args,
	}
	body, err := json.Marshal(reqBody)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}
	req := httptest.NewRequest(http.MethodPost, "/invoke", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()
	invokeHandler(rr, req)
	return rr
}

// Helper to decode response
func decodeResponse(t *testing.T, rr *httptest.ResponseRecorder) telepathy.OmniResponse {
	t.Helper()
	var res telepathy.OmniResponse
	if err := json.NewDecoder(rr.Body).Decode(&res); err != nil {
		t.Fatalf("Failed to decode response: %v (body: %s)", err, rr.Body.String())
	}
	return res
}

// ── HEALTH ENDPOINT ──────────────────────────────────────────────

func TestHealthEndpoint(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rr := httptest.NewRecorder()
	healthHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("Expected 200, got %d", rr.Code)
	}

	var body map[string]interface{}
	if err := json.NewDecoder(rr.Body).Decode(&body); err != nil {
		t.Fatalf("Failed to decode health response: %v", err)
	}
	if body["status"] != "Ok" {
		t.Errorf("Expected status Ok, got %v", body["status"])
	}
	t.Logf("✅ Health endpoint: %v", body)
}

// ── READINESS ENDPOINT ──────────────────────────────────────────

func TestReadinessEndpoint(t *testing.T) {
	// Set gateway as ready
	gatewayReady = 1

	req := httptest.NewRequest(http.MethodGet, "/readiness", nil)
	rr := httptest.NewRecorder()
	readinessHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("Expected 200, got %d", rr.Code)
	}

	var body map[string]interface{}
	json.NewDecoder(rr.Body).Decode(&body)
	if body["ready"] != true {
		t.Errorf("Expected ready=true, got %v", body["ready"])
	}
	t.Logf("✅ Readiness probe: %v", body)
}

// ── METRICS ENDPOINT ──────────────────────────────────────────────

func TestMetricsEndpoint(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rr := httptest.NewRecorder()
	metricsHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("Expected 200, got %d", rr.Code)
	}

	var body map[string]interface{}
	json.NewDecoder(rr.Body).Decode(&body)

	required := []string{"uptime_seconds", "total_requests", "goroutines", "heap_alloc_mb", "telepathy_routes", "cloud_api_wrappers", "ai_models"}
	for _, key := range required {
		if _, ok := body[key]; !ok {
			t.Errorf("Missing metrics key: %s", key)
		}
	}
	t.Logf("✅ Metrics: routes=%.0f, wrappers=%.0f, models=%.0f",
		body["telepathy_routes"], body["cloud_api_wrappers"], body["ai_models"])
}

// ── METHOD NOT ALLOWED ──────────────────────────────────────────

func TestInvokeRejectsGET(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/invoke", nil)
	rr := httptest.NewRecorder()
	invokeHandler(rr, req)

	if rr.Code != http.StatusMethodNotAllowed {
		t.Fatalf("Expected 405, got %d", rr.Code)
	}
	t.Logf("✅ GET /invoke correctly rejected with 405")
}

// ── INVALID JSON BODY ───────────────────────────────────────────

func TestInvokeRejectsInvalidJSON(t *testing.T) {
	req := httptest.NewRequest(http.MethodPost, "/invoke", bytes.NewReader([]byte("not json")))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()
	invokeHandler(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Fatalf("Expected 400, got %d", rr.Code)
	}
	t.Logf("✅ Invalid JSON correctly rejected with 400")
}

// ── UNKNOWN METHOD FALLBACK ─────────────────────────────────────

func TestInvokeUnknownMethod(t *testing.T) {
	rr := invokeTelepathy(t, "nonexistent::method::xyz", nil)
	res := decodeResponse(t, rr)

	if res.Status != "Err" {
		t.Errorf("Expected Err for unknown method, got %s", res.Status)
	}
	if res.Error == "" {
		t.Error("Expected error message for unknown method")
	}
	t.Logf("✅ Unknown method correctly returns Err: %s", res.Error)
}

// ── MODEL ZOO: LIST ALL ─────────────────────────────────────────

func TestModelZooListAll(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::ListAll", map[string]interface{}{})
	res := decodeResponse(t, rr)

	if res.Status != "Ok" {
		t.Fatalf("Expected Ok, got %s (error: %s)", res.Status, res.Error)
	}

	data, ok := res.Data.(map[string]interface{})
	if !ok {
		t.Fatalf("Expected map data, got %T", res.Data)
	}

	count, _ := data["count"].(float64)
	if count < 15 {
		t.Errorf("Expected at least 15 models, got %.0f", count)
	}
	t.Logf("✅ ModelZoo ListAll: %.0f models registered", count)
}

// ── MODEL ZOO: GET INFO ─────────────────────────────────────────

func TestModelZooGetInfo(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::GetInfo", map[string]interface{}{
		"modelId": "gemini-pro",
	})
	res := decodeResponse(t, rr)

	if res.Status != "Ok" {
		t.Fatalf("Expected Ok, got %s (error: %s)", res.Status, res.Error)
	}

	data, ok := res.Data.(map[string]interface{})
	if !ok {
		t.Fatalf("Expected map data, got %T", res.Data)
	}

	if data["id"] != "gemini-pro" {
		t.Errorf("Expected model id 'gemini-pro', got %v", data["id"])
	}
	t.Logf("✅ ModelZoo GetInfo: %s (%s) → %s", data["name"], data["tier"], data["endpoint"])
}

// ── MODEL ZOO: GET INFO — NOT FOUND ─────────────────────────────

func TestModelZooGetInfoNotFound(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::GetInfo", map[string]interface{}{
		"modelId": "nonexistent-model",
	})
	res := decodeResponse(t, rr)

	if res.Status != "Err" {
		t.Errorf("Expected Err for nonexistent model, got %s", res.Status)
	}
	t.Logf("✅ ModelZoo GetInfo correctly returns Err for unknown model")
}

// ── MODEL ZOO: LIST TIERS ───────────────────────────────────────

func TestModelZooListTiers(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::ListTiers", map[string]interface{}{})
	res := decodeResponse(t, rr)

	if res.Status != "Ok" {
		t.Fatalf("Expected Ok, got %s (error: %s)", res.Status, res.Error)
	}

	data, ok := res.Data.(map[string]interface{})
	if !ok {
		t.Fatalf("Expected map data, got %T", res.Data)
	}

	totalModels, _ := data["total_models"].(float64)
	if totalModels < 15 {
		t.Errorf("Expected at least 15 total models, got %.0f", totalModels)
	}
	t.Logf("✅ ModelZoo ListTiers: %.0f total models across tiers", totalModels)
}

// ── MODEL ZOO: INVOKE ───────────────────────────────────────────

func TestModelZooInvoke(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::Invoke", map[string]interface{}{
		"modelId": "gemini-flash",
		"prompt":  "Explain quantum computing in 3 sentences",
	})
	res := decodeResponse(t, rr)

	if res.Status != "Ok" {
		t.Fatalf("Expected Ok, got %s (error: %s)", res.Status, res.Error)
	}

	data, ok := res.Data.(map[string]interface{})
	if !ok {
		t.Fatalf("Expected map data, got %T", res.Data)
	}

	if data["status"] != "INVOCATION_ROUTED" {
		t.Errorf("Expected INVOCATION_ROUTED, got %v", data["status"])
	}
	t.Logf("✅ ModelZoo Invoke: %s → %s (%s)", data["model"], data["endpoint"], data["status"])
}

// ── MODEL ZOO: FILTER BY TIER ───────────────────────────────────

func TestModelZooFilterByTier(t *testing.T) {
	rr := invokeTelepathy(t, "omni::models::ListAll", map[string]interface{}{
		"tier": "llm",
	})
	res := decodeResponse(t, rr)

	if res.Status != "Ok" {
		t.Fatalf("Expected Ok, got %s", res.Status)
	}

	data, ok := res.Data.(map[string]interface{})
	if !ok {
		t.Fatalf("Expected map data, got %T", res.Data)
	}

	count, _ := data["count"].(float64)
	if count < 4 {
		t.Errorf("Expected at least 4 LLM models, got %.0f", count)
	}
	t.Logf("✅ ModelZoo Filter: tier=llm → %.0f models", count)
}
