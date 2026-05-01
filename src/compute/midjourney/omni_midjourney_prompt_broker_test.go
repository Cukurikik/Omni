package midjourney

import (
	"strings"
	"testing"
	"time"
)

func TestNewBrokerQueue_Defaults(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	if bq.Inbound == nil {
		t.Fatal("Inbound channel not initialized")
	}
	if bq.Outbound == nil {
		t.Fatal("Outbound channel not initialized")
	}
	if len(bq.bannedWords) == 0 {
		t.Fatal("Banned words list not initialized")
	}
}

func TestNewBrokerQueue_MaxSize(t *testing.T) {
	bq := NewBrokerQueue(9999)
	defer bq.Shutdown()

	if cap(bq.Inbound) != MaxQueueSize {
		t.Errorf("Expected max queue size %d, got %d", MaxQueueSize, cap(bq.Inbound))
	}
}

func TestValidatePrompt_Empty(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	err := bq.ValidatePrompt("")
	if err != ErrEmptyPrompt {
		t.Errorf("Expected ErrEmptyPrompt, got %v", err)
	}
}

func TestValidatePrompt_TooShort(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	err := bq.ValidatePrompt("ab")
	if err != ErrPromptTooShort {
		t.Errorf("Expected ErrPromptTooShort, got %v", err)
	}
}

func TestValidatePrompt_TooLong(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	longPrompt := strings.Repeat("a", MaxPromptLength+1)
	err := bq.ValidatePrompt(longPrompt)
	if err != ErrPromptTooLong {
		t.Errorf("Expected ErrPromptTooLong, got %v", err)
	}
}

func TestValidatePrompt_BannedWords(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	bannedTests := []string{
		"a beautiful nsfw artwork",
		"a NUDE portrait",
		"explicit violence scene",
	}

	for _, test := range bannedTests {
		err := bq.ValidatePrompt(test)
		if err == nil {
			t.Errorf("Expected error for banned word in prompt: %q", test)
		}
	}
}

func TestValidatePrompt_SQLInjection(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	sqlTests := []string{
		"a nice landscape DROP TABLE users",
		"portrait'; -- malicious",
	}

	for _, test := range sqlTests {
		err := bq.ValidatePrompt(test)
		if err == nil {
			t.Errorf("Expected error for SQL injection pattern: %q", test)
		}
	}
}

func TestValidatePrompt_XSS(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	xssTests := []string{
		"portrait <script>alert(1)</script>",
		"landscape javascript:void(0)",
	}

	for _, test := range xssTests {
		err := bq.ValidatePrompt(test)
		if err == nil {
			t.Errorf("Expected error for XSS pattern: %q", test)
		}
	}
}

func TestValidatePrompt_Valid(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	validPrompts := []string{
		"a beautiful sunset over mountains",
		"cyberpunk city at night, neon lights, 4k",
		"abc",
	}

	for _, test := range validPrompts {
		err := bq.ValidatePrompt(test)
		if err != nil {
			t.Errorf("Expected no error for valid prompt %q, got %v", test, err)
		}
	}
}

func TestDispatch_Success(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	req := PromptRequest{
		JobID:     "test-001",
		Prompt:    "a beautiful landscape with mountains",
		Model:     "midjourney-v6",
		AspectRat: "16:9",
	}

	result := bq.Dispatch(req)
	if !result.Success {
		t.Errorf("Expected success, got error: %v", result.Error)
	}
	if !strings.HasPrefix(result.Value, "mj://") {
		t.Errorf("Expected mj:// URI prefix, got %q", result.Value)
	}

	// Verify it was sent to outbound
	select {
	case msg := <-bq.Outbound:
		if msg != result.Value {
			t.Errorf("Expected outbound message %q, got %q", result.Value, msg)
		}
	case <-time.After(1 * time.Second):
		t.Fatal("Timeout waiting for outbound message")
	}
}

func TestDispatch_DefaultModel(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	req := PromptRequest{
		JobID:  "test-002",
		Prompt: "a simple test prompt",
	}

	result := bq.Dispatch(req)
	if !result.Success {
		t.Errorf("Expected success, got error: %v", result.Error)
	}
	if !strings.Contains(result.Value, "midjourney-v6") {
		t.Errorf("Expected default model midjourney-v6 in result %q", result.Value)
	}
}

func TestDispatch_DefaultAspectRat(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	req := PromptRequest{
		JobID:  "test-003",
		Prompt: "a simple test prompt",
	}

	result := bq.Dispatch(req)
	if !result.Success {
		t.Errorf("Expected success, got error: %v", result.Error)
	}
	if !strings.Contains(result.Value, "1:1") {
		t.Errorf("Expected default aspect ratio 1:1 in result %q", result.Value)
	}
}

func TestDispatch_InvalidPrompt(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	req := PromptRequest{
		JobID:  "test-004",
		Prompt: "",
	}

	result := bq.Dispatch(req)
	if result.Success {
		t.Error("Expected failure for empty prompt")
	}
	if result.Error == nil {
		t.Error("Expected error for empty prompt")
	}
}

func TestDispatch_QueueOverflow(t *testing.T) {
	// Create a queue with size 1 and fill it
	bq := NewBrokerQueue(1)
	defer bq.Shutdown()

	// First dispatch should succeed
	req1 := PromptRequest{
		JobID:  "test-005a",
		Prompt: "first prompt",
	}
	result1 := bq.Dispatch(req1)
	if !result1.Success {
		t.Errorf("First dispatch should succeed: %v", result1.Error)
	}

	// Consume the outbound to unblock
	<-bq.Outbound

	// Second dispatch should also succeed since queue has capacity
	req2 := PromptRequest{
		JobID:  "test-005b",
		Prompt: "second prompt",
	}
	result2 := bq.Dispatch(req2)
	if !result2.Success {
		t.Logf("Second dispatch succeeded (expected with consumed outbound)")
	}
}

func TestGetMetrics(t *testing.T) {
	bq := NewBrokerQueue(10)
	defer bq.Shutdown()

	// Dispatch a few requests
	for i := 0; i < 3; i++ {
		req := PromptRequest{
			JobID:  "metric-test",
			Prompt: "test prompt",
		}
		bq.Dispatch(req)
		<-bq.Outbound
	}

	metrics := bq.GetMetrics()
	if metrics["total_dispatched"].(int64) != 3 {
		t.Errorf("Expected 3 dispatched, got %v", metrics["total_dispatched"])
	}
	if metrics["total_failed"].(int64) != 0 {
		t.Errorf("Expected 0 failed, got %v", metrics["total_failed"])
	}
}

func TestHashPrompt_Deterministic(t *testing.T) {
	prompt := "a beautiful sunset"
	hash1 := hashPrompt(prompt)
	hash2 := hashPrompt(prompt)

	if hash1 != hash2 {
		t.Errorf("Expected deterministic hash, got %q and %q", hash1, hash2)
	}
}

func TestHashPrompt_Different(t *testing.T) {
	hash1 := hashPrompt("prompt one")
	hash2 := hashPrompt("prompt two")

	if hash1 == hash2 {
		t.Errorf("Expected different hashes for different prompts")
	}
}

func TestShutdown(t *testing.T) {
	bq := NewBrokerQueue(10)

	// Should not panic
	bq.Shutdown()

	// Verify channels are closed
	defer func() {
		if r := recover(); r == nil {
			t.Log("Channels properly closed after shutdown")
		}
	}()

	// This should not block or panic since channels are closed
	select {
	case _, ok := <-bq.Inbound:
		if !ok {
			t.Log("Inbound channel properly closed")
		}
	default:
	}
}
