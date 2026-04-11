package models

import (
	"context"
	"testing"
)

// ==========================================
// 🧪 OMNI AI MODEL ZOO — REGISTRY TESTS
// ==========================================

func TestRegistrySingleton(t *testing.T) {
	r1 := GetRegistry()
	r2 := GetRegistry()

	if r1 != r2 {
		t.Fatalf("Registry should be singleton, got different instances")
	}
	t.Log("✅ Registry singleton verified")
}

func TestRegistryInitialize(t *testing.T) {
	r := GetRegistry()
	err := r.Initialize("omni-tool-9c48b", "test-key", "us-central1")
	if err != nil {
		t.Fatalf("Initialize failed: %v", err)
	}

	count := r.Count()
	if count < 20 {
		t.Fatalf("Expected 20+ models registered, got %d", count)
	}

	t.Logf("✅ Registry initialized with %d models", count)
}

func TestGetModel(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	tests := []struct {
		modelID     string
		displayName string
		tier        ModelTier
	}{
		{"transformer-base", "Transformer Base", TierFoundation},
		{"bert-base", "BERT (Bidirectional Encoder)", TierFoundation},
		{"t5-base", "T5 (Text-to-Text Transfer Transformer)", TierFoundation},
		{"lamda-v2", "LaMDA v2 (via Gemini)", TierLLM},
		{"palm-2", "PaLM 2", TierLLM},
		{"gemini-pro", "Gemini 2.5 Pro", TierLLM},
		{"gemini-ultra", "Gemini Ultra", TierLLM},
		{"gemini-flash", "Gemini 2.5 Flash", TierLLM},
		{"gemini-nano", "Gemini Nano", TierLLM},
		{"gemma-2", "Gemma 2", TierOpenWeights},
		{"gemma-3", "Gemma 3", TierOpenWeights},
		{"gemma-4", "Gemma 4", TierOpenWeights},
		{"code-gemma", "CodeGemma", TierOpenWeights},
		{"recurrent-gemma", "RecurrentGemma", TierOpenWeights},
		{"imagen-3", "Imagen 3", TierGenerativeMedia},
		{"veo-2", "Veo 2", TierGenerativeMedia},
		{"musiclm", "MusicLM / Lyria", TierGenerativeMedia},
		{"vit-base", "Vision Transformer (ViT)", TierVisionSpeech},
		{"usm-chirp", "Universal Speech Model (USM/Chirp)", TierVisionSpeech},
	}

	for _, tt := range tests {
		t.Run(tt.modelID, func(t *testing.T) {
			spec, err := r.Get(tt.modelID)
			if err != nil {
				t.Fatalf("Model '%s' not found: %v", tt.modelID, err)
			}

			if spec.DisplayName != tt.displayName {
				t.Errorf("Expected display name '%s', got '%s'", tt.displayName, spec.DisplayName)
			}

			if spec.Tier != tt.tier {
				t.Errorf("Expected tier %s, got %s", tt.tier, spec.Tier)
			}

			t.Logf("✅ %s → %s (Tier: %s)", tt.modelID, spec.DisplayName, spec.Tier)
		})
	}
}

func TestModelNotFound(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	_, err := r.Get("nonexistent-model")
	if err == nil {
		t.Fatal("Expected error for nonexistent model")
	}

	regErr, ok := err.(*ModelRegistryError)
	if !ok {
		t.Fatal("Expected ModelRegistryError type")
	}

	if regErr.Code != "MODEL_NOT_FOUND" {
		t.Errorf("Expected code MODEL_NOT_FOUND, got %s", regErr.Code)
	}

	t.Logf("✅ Model not found error: %s", regErr)
}

func TestListByTier(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	tiers := map[ModelTier]int{
		TierFoundation:      3, // Transformer, BERT, T5
		TierLLM:             5, // LaMDA, PaLM, Gemini Pro/Ultra/Flash/Nano
		TierOpenWeights:     5, // Gemma 2/3/4, CodeGemma, RecurrentGemma
		TierGenerativeMedia: 4, // Imagen 3, Imagen Edit, Veo 2, MusicLM
		TierVisionSpeech:    2, // ViT, USM
	}

	for tier, expectedMin := range tiers {
		models := r.ListByTier(tier)
		if len(models) < expectedMin {
			t.Errorf("Tier %s: expected at least %d models, got %d", tier, expectedMin, len(models))
		}
		t.Logf("✅ Tier %s: %d models", tier, len(models))
	}
}

func TestListByCapability(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	capTests := []struct {
		cap      ModelCapability
		name     string
		minCount int
	}{
		{CapTextGeneration, "TextGeneration", 10},
		{CapCodeGeneration, "CodeGeneration", 3},
		{CapImageGeneration, "ImageGeneration", 2},
		{CapMultimodal, "Multimodal", 4},
		{CapConversation, "Conversation", 5},
		{CapFineTuning, "FineTuning", 4},
		{CapSpeechRecognition, "SpeechRecognition", 1},
	}

	for _, tc := range capTests {
		models := r.ListByCapability(tc.cap)
		if len(models) < tc.minCount {
			t.Errorf("Capability %s: expected at least %d models, got %d", tc.name, tc.minCount, len(models))
		}
		t.Logf("✅ Capability %s: %d models", tc.name, len(models))
	}
}

func TestResolveEndpoint(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	endpointTests := []struct {
		modelID  string
		contains string
	}{
		{"gemini-pro", "generativelanguage.googleapis.com"},
		{"gemini-flash", "generativelanguage.googleapis.com"},
		{"palm-2", "aiplatform.googleapis.com"},
		{"imagen-3", "aiplatform.googleapis.com"},
		{"vit-base", "vision.googleapis.com"},
		{"usm-chirp", "speech.googleapis.com"},
	}

	for _, tc := range endpointTests {
		endpoint, err := r.ResolveEndpoint(tc.modelID)
		if err != nil {
			t.Fatalf("ResolveEndpoint(%s) failed: %v", tc.modelID, err)
		}

		found := false
		if len(endpoint) > 0 {
			for i := 0; i <= len(endpoint)-len(tc.contains); i++ {
				if endpoint[i:i+len(tc.contains)] == tc.contains {
					found = true
					break
				}
			}
		}

		if !found {
			t.Errorf("Endpoint for %s should contain '%s', got '%s'", tc.modelID, tc.contains, endpoint)
		}

		t.Logf("✅ %s → %s", tc.modelID, endpoint)
	}
}

func TestInvokeGeminiFlash(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	ctx := context.Background()
	resp, err := r.Invoke(ctx, &InferenceRequest{
		ModelID:         "gemini-flash",
		Prompt:          "Hello from OMNI Model Zoo test",
		Temperature:     0.5,
		MaxOutputTokens: 100,
	})

	if err != nil {
		t.Fatalf("Invoke gemini-flash failed: %v", err)
	}

	if resp.ModelID != "gemini-flash" {
		t.Errorf("Expected ModelID 'gemini-flash', got '%s'", resp.ModelID)
	}

	if resp.Latency < 0 {
		t.Error("Expected non-negative latency")
	}

	t.Logf("✅ Gemini Flash invoked: latency=%v, model=%s", resp.Latency, resp.ModelID)
}

func TestMultimodalModels(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	multimodals := r.ListByCapability(CapMultimodal)
	for _, m := range multimodals {
		if !m.IsMultimodal {
			t.Errorf("Model %s has multimodal capability but IsMultimodal=false", m.ID)
		}
		t.Logf("✅ Multimodal: %s (%s) — %s", m.DisplayName, m.Parameters, m.Tier)
	}
}

func TestOpenWeightModels(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	openWeights := r.ListByTier(TierOpenWeights)
	for _, m := range openWeights {
		if !m.IsOpenWeight {
			t.Errorf("Model %s is in OpenWeights tier but IsOpenWeight=false", m.ID)
		}
		t.Logf("✅ Open-Weight: %s (%s)", m.DisplayName, m.Parameters)
	}
}

func TestTierString(t *testing.T) {
	tests := []struct {
		tier     ModelTier
		expected string
	}{
		{TierFoundation, "Foundation"},
		{TierLLM, "LLM"},
		{TierOpenWeights, "Open-Weights"},
		{TierGenerativeMedia, "Generative-Media"},
		{TierVisionSpeech, "Vision-Speech"},
	}

	for _, tc := range tests {
		if tc.tier.String() != tc.expected {
			t.Errorf("Tier.String() = %s, want %s", tc.tier.String(), tc.expected)
		}
	}
	t.Log("✅ All tier strings correct")
}

func TestListAll(t *testing.T) {
	r := GetRegistry()
	_ = r.Initialize("omni-tool-9c48b", "test-key", "us-central1")

	all := r.ListAll()
	count := r.Count()

	if len(all) != count {
		t.Errorf("ListAll returned %d, Count returned %d", len(all), count)
	}

	t.Logf("✅ Total models in OMNI Model Zoo: %d", count)

	// Print full catalog
	t.Log("\n📋 OMNI AI MODEL ZOO — FULL CATALOG:")
	for _, m := range all {
		t.Logf("  [%s] %s | %s | %s | Multimodal=%v",
			m.Tier, m.DisplayName, m.GCPModelID, m.Parameters, m.IsMultimodal)
	}
}
