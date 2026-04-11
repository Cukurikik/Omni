package models

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"
)

// ==========================================
// 🧠 OMNI AI MODEL ZOO — CENTRAL REGISTRY
// ==========================================
// Unified model registry that routes inference requests
// to the correct GCP endpoint (Gemini API, Vertex AI,
// Model Garden, Vision API, Speech API, etc.)
//
// Architecture: Factory Pattern → Model Router → GCP Endpoint
// Supports 20+ AI models across 5 tiers.

// ModelTier classifies models by their capability tier
type ModelTier int

const (
	TierFoundation     ModelTier = iota // Tier 1: Transformer, BERT, T5
	TierLLM                            // Tier 2: LaMDA, PaLM, Gemini
	TierOpenWeights                    // Tier 3: Gemma, CodeGemma, RecurrentGemma
	TierGenerativeMedia                // Tier 4: Imagen, Veo, MusicLM
	TierVisionSpeech                   // Tier 5: ViT, USM
)

// String returns human-readable tier name
func (t ModelTier) String() string {
	switch t {
	case TierFoundation:
		return "Foundation"
	case TierLLM:
		return "LLM"
	case TierOpenWeights:
		return "Open-Weights"
	case TierGenerativeMedia:
		return "Generative-Media"
	case TierVisionSpeech:
		return "Vision-Speech"
	default:
		return "Unknown"
	}
}

// ModelCapability defines what a model can do
type ModelCapability int

const (
	CapTextGeneration    ModelCapability = 1 << iota // Generate text
	CapTextEmbedding                                 // Create text embeddings
	CapImageGeneration                               // Generate images from text
	CapImageUnderstanding                            // Understand/classify images
	CapVideoGeneration                               // Generate video from text
	CapVideoUnderstanding                            // Analyze video content
	CapAudioGeneration                               // Generate audio/music
	CapSpeechRecognition                             // Speech-to-text
	CapSpeechSynthesis                               // Text-to-speech
	CapCodeGeneration                                // Generate/complete code
	CapMultimodal                                    // Native multimodal
	CapConversation                                  // Multi-turn dialogue
	CapReasoning                                     // Chain-of-thought reasoning
	CapTranslation                                   // Language translation
	CapFineTuning                                    // Supports fine-tuning
)

// ModelEndpointType defines the GCP routing strategy
type ModelEndpointType int

const (
	EndpointGeminiAPI    ModelEndpointType = iota // Gemini REST API (generativelanguage.googleapis.com)
	EndpointVertexAI                             // Vertex AI Prediction (aiplatform.googleapis.com)
	EndpointModelGarden                          // Vertex AI Model Garden (pre-deployed)
	EndpointVisionAPI                            // Cloud Vision API
	EndpointSpeechAPI                            // Cloud Speech-to-Text V2
	EndpointCustomDeploy                         // Custom container deployment
)

// ModelSpec defines a registered AI model's metadata and routing
type ModelSpec struct {
	ID            string            // Unique model identifier (e.g., "gemini-pro")
	DisplayName   string            // Human-readable name
	Version       string            // Model version
	Tier          ModelTier         // Classification tier
	Endpoint      ModelEndpointType // Where to route requests
	GCPModelID    string            // GCP-specific model ID for API calls
	Region        string            // Default region
	Capabilities  ModelCapability   // Bitmask of capabilities
	MaxTokens     int               // Maximum output tokens
	MaxImageSize  int               // Max image dimension (px) for vision models
	Languages     int               // Number of supported languages
	Parameters    string            // Model size (e.g., "175B", "9B")
	Description   string            // Brief description
	CostPerMToken float64           // Cost per million tokens (USD)
	IsMultimodal  bool              // Native multimodal support
	IsOpenWeight  bool              // Open-weight model
	CreatedAt     time.Time         // Registration timestamp
}

// InferenceRequest is the unified input for any model
type InferenceRequest struct {
	ModelID       string            // Which model to use
	Prompt        string            // Text prompt
	SystemPrompt  string            // System instructions
	ImageData     []byte            // Image input (for multimodal)
	AudioData     []byte            // Audio input
	VideoData     []byte            // Video input
	Temperature   float32           // Creativity control (0.0 - 2.0)
	MaxOutputTokens int             // Maximum tokens to generate
	TopP          float32           // Nucleus sampling
	TopK          int               // Top-K sampling
	StopSequences []string          // Stop generation tokens
	Metadata      map[string]string // Custom metadata
}

// InferenceResponse is the unified output from any model
type InferenceResponse struct {
	ModelID        string        // Which model responded
	Text           string        // Generated text
	ImageBytes     []byte        // Generated image (for Imagen)
	AudioBytes     []byte        // Generated audio (for MusicLM)
	VideoBytes     []byte        // Generated video (for Veo)
	Embeddings     []float64     // Vector embeddings (for BERT)
	TokensUsed     int           // Total tokens consumed
	PromptTokens   int           // Input tokens
	OutputTokens   int           // Output tokens
	Latency        time.Duration // Request latency
	CostEstimate   float64       // Estimated cost in USD
	FinishReason   string        // Why generation stopped
	SafetyRatings  []SafetyRating
	Metadata       map[string]string
}

// SafetyRating from Google's safety filters
type SafetyRating struct {
	Category    string  // e.g., "HARM_CATEGORY_HATE_SPEECH"
	Probability string  // e.g., "LOW", "MEDIUM", "HIGH"
	Score       float64 // Numeric confidence
	Blocked     bool    // Whether content was blocked
}

// ModelRegistryError implements monadic error handling
type ModelRegistryError struct {
	Code    string
	Message string
	ModelID string
}

func (e *ModelRegistryError) Error() string {
	return fmt.Sprintf("OMNI-ModelZoo[%s]: %s (model=%s)", e.Code, e.Message, e.ModelID)
}

// ==========================================
// 🏭 REGISTRY — FACTORY & ROUTER
// ==========================================

// Registry is the central model registry (singleton)
type Registry struct {
	mu       sync.RWMutex
	models   map[string]*ModelSpec
	projectID string
	apiKey    string
	region    string
}

var (
	globalRegistry *Registry
	registryOnce   sync.Once
)

// GetRegistry returns the singleton registry instance
func GetRegistry() *Registry {
	registryOnce.Do(func() {
		globalRegistry = &Registry{
			models: make(map[string]*ModelSpec),
		}
	})
	return globalRegistry
}

// Initialize sets up the registry with GCP credentials
func (r *Registry) Initialize(projectID, apiKey, region string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.projectID = projectID
	r.apiKey = apiKey
	r.region = region

	// Register all 20+ models
	r.registerAllModels()

	log.Printf("🧠 [OMNI MODEL ZOO] Registry initialized: %d models registered", len(r.models))
	log.Printf("🧠 [OMNI MODEL ZOO] Project: %s | Region: %s", projectID, region)
	return nil
}

// Register adds a model to the registry
func (r *Registry) Register(spec *ModelSpec) {
	spec.CreatedAt = time.Now()
	r.models[spec.ID] = spec
}

// Get retrieves a model spec by ID
func (r *Registry) Get(modelID string) (*ModelSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	spec, ok := r.models[modelID]
	if !ok {
		return nil, &ModelRegistryError{
			Code:    "MODEL_NOT_FOUND",
			Message: fmt.Sprintf("model '%s' is not registered in OMNI Model Zoo", modelID),
			ModelID: modelID,
		}
	}
	return spec, nil
}

// ListByTier returns all models in a specific tier
func (r *Registry) ListByTier(tier ModelTier) []*ModelSpec {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*ModelSpec
	for _, spec := range r.models {
		if spec.Tier == tier {
			result = append(result, spec)
		}
	}
	return result
}

// ListByCapability returns models that have a specific capability
func (r *Registry) ListByCapability(cap ModelCapability) []*ModelSpec {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*ModelSpec
	for _, spec := range r.models {
		if spec.Capabilities&cap != 0 {
			result = append(result, spec)
		}
	}
	return result
}

// ListAll returns all registered models
func (r *Registry) ListAll() []*ModelSpec {
	r.mu.RLock()
	defer r.mu.RUnlock()

	result := make([]*ModelSpec, 0, len(r.models))
	for _, spec := range r.models {
		result = append(result, spec)
	}
	return result
}

// Count returns total registered models
func (r *Registry) Count() int {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return len(r.models)
}

// HasCapability checks if a model supports a capability
func (r *Registry) HasCapability(modelID string, cap ModelCapability) bool {
	spec, err := r.Get(modelID)
	if err != nil {
		return false
	}
	return spec.Capabilities&cap != 0
}

// ResolveEndpoint returns the GCP API endpoint URL for a model
func (r *Registry) ResolveEndpoint(modelID string) (string, error) {
	spec, err := r.Get(modelID)
	if err != nil {
		return "", err
	}

	switch spec.Endpoint {
	case EndpointGeminiAPI:
		return fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/%s", spec.GCPModelID), nil
	case EndpointVertexAI:
		return fmt.Sprintf("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/publishers/google/models/%s",
			spec.Region, r.projectID, spec.Region, spec.GCPModelID), nil
	case EndpointModelGarden:
		return fmt.Sprintf("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints/%s",
			spec.Region, r.projectID, spec.Region, spec.GCPModelID), nil
	case EndpointVisionAPI:
		return "https://vision.googleapis.com/v1/images:annotate", nil
	case EndpointSpeechAPI:
		return fmt.Sprintf("https://speech.googleapis.com/v2/projects/%s/locations/global/recognizers/_", r.projectID), nil
	case EndpointCustomDeploy:
		return fmt.Sprintf("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints/%s:predict",
			spec.Region, r.projectID, spec.Region, spec.GCPModelID), nil
	default:
		return "", &ModelRegistryError{
			Code:    "UNKNOWN_ENDPOINT",
			Message: "cannot resolve endpoint type",
			ModelID: modelID,
		}
	}
}

// Invoke routes an inference request to the correct GCP endpoint
func (r *Registry) Invoke(ctx context.Context, req *InferenceRequest) (*InferenceResponse, error) {
	start := time.Now()

	spec, err := r.Get(req.ModelID)
	if err != nil {
		return nil, err
	}

	log.Printf("🧠 [MODEL ZOO] Routing '%s' (%s) → %s endpoint",
		spec.DisplayName, spec.Tier, endpointName(spec.Endpoint))

	// Set defaults
	if req.Temperature == 0 {
		req.Temperature = 0.7
	}
	if req.MaxOutputTokens == 0 {
		req.MaxOutputTokens = 1024
	}

	// Route to correct handler based on endpoint type
	var resp *InferenceResponse
	switch spec.Endpoint {
	case EndpointGeminiAPI:
		resp, err = r.invokeGeminiAPI(ctx, spec, req)
	case EndpointVertexAI, EndpointModelGarden, EndpointCustomDeploy:
		resp, err = r.invokeVertexAI(ctx, spec, req)
	case EndpointVisionAPI:
		resp, err = r.invokeVisionAPI(ctx, spec, req)
	case EndpointSpeechAPI:
		resp, err = r.invokeSpeechAPI(ctx, spec, req)
	default:
		return nil, &ModelRegistryError{
			Code:    "UNROUTABLE",
			Message: "no handler for endpoint type",
			ModelID: req.ModelID,
		}
	}

	if err != nil {
		return nil, err
	}

	resp.ModelID = req.ModelID
	resp.Latency = time.Since(start)
	return resp, nil
}

// invokeGeminiAPI sends request to Gemini REST API
func (r *Registry) invokeGeminiAPI(ctx context.Context, spec *ModelSpec, req *InferenceRequest) (*InferenceResponse, error) {
	endpoint, _ := r.ResolveEndpoint(spec.ID)
	log.Printf("🌐 [GEMINI API] → %s", endpoint)

	// Real implementation would use HTTP client with API key
	// This is the routing skeleton — actual HTTP calls are in vertex_ai_models.go
	return &InferenceResponse{
		Text:         fmt.Sprintf("[OMNI-ModelZoo] Gemini API response from %s", spec.GCPModelID),
		FinishReason: "STOP",
	}, nil
}

// invokeVertexAI sends request to Vertex AI endpoint
func (r *Registry) invokeVertexAI(ctx context.Context, spec *ModelSpec, req *InferenceRequest) (*InferenceResponse, error) {
	endpoint, _ := r.ResolveEndpoint(spec.ID)
	log.Printf("🌐 [VERTEX AI] → %s", endpoint)

	return &InferenceResponse{
		Text:         fmt.Sprintf("[OMNI-ModelZoo] Vertex AI response from %s", spec.GCPModelID),
		FinishReason: "STOP",
	}, nil
}

// invokeVisionAPI sends request to Cloud Vision API
func (r *Registry) invokeVisionAPI(ctx context.Context, spec *ModelSpec, req *InferenceRequest) (*InferenceResponse, error) {
	log.Printf("👁️ [VISION API] Processing image through %s", spec.DisplayName)

	return &InferenceResponse{
		Text:         fmt.Sprintf("[OMNI-ModelZoo] Vision API response from %s", spec.GCPModelID),
		FinishReason: "STOP",
	}, nil
}

// invokeSpeechAPI sends request to Cloud Speech-to-Text API
func (r *Registry) invokeSpeechAPI(ctx context.Context, spec *ModelSpec, req *InferenceRequest) (*InferenceResponse, error) {
	log.Printf("🎤 [SPEECH API] Processing audio through %s", spec.DisplayName)

	return &InferenceResponse{
		Text:         fmt.Sprintf("[OMNI-ModelZoo] Speech API response from %s", spec.GCPModelID),
		FinishReason: "STOP",
	}, nil
}

func endpointName(e ModelEndpointType) string {
	switch e {
	case EndpointGeminiAPI:
		return "Gemini-API"
	case EndpointVertexAI:
		return "Vertex-AI"
	case EndpointModelGarden:
		return "Model-Garden"
	case EndpointVisionAPI:
		return "Vision-API"
	case EndpointSpeechAPI:
		return "Speech-API"
	case EndpointCustomDeploy:
		return "Custom-Deploy"
	default:
		return "Unknown"
	}
}

// ==========================================
// 📋 MODEL REGISTRATION TABLE
// ==========================================

func (r *Registry) registerAllModels() {
	// ── TIER 1: FOUNDATION ──
	r.Register(&ModelSpec{
		ID: "transformer-base", DisplayName: "Transformer Base",
		Version: "1.0", Tier: TierFoundation, Endpoint: EndpointVertexAI,
		GCPModelID: "transformer-base", Region: "us-central1",
		Capabilities: CapTextGeneration | CapTextEmbedding,
		MaxTokens: 512, Parameters: "110M",
		Description: "Original Transformer architecture (Attention Is All You Need)",
	})
	r.Register(&ModelSpec{
		ID: "bert-base", DisplayName: "BERT (Bidirectional Encoder)",
		Version: "2.0", Tier: TierFoundation, Endpoint: EndpointVertexAI,
		GCPModelID: "textembedding-gecko@003", Region: "us-central1",
		Capabilities: CapTextEmbedding | CapTextGeneration,
		MaxTokens: 512, Parameters: "340M", Languages: 104,
		Description: "Bidirectional understanding of language context",
	})
	r.Register(&ModelSpec{
		ID: "t5-base", DisplayName: "T5 (Text-to-Text Transfer Transformer)",
		Version: "1.1", Tier: TierFoundation, Endpoint: EndpointVertexAI,
		GCPModelID: "text-unicorn@001", Region: "us-central1",
		Capabilities: CapTextGeneration | CapTranslation,
		MaxTokens: 1024, Parameters: "11B",
		Description: "All NLP tasks as text-to-text format",
	})

	// ── TIER 2: LLM ERA ──
	r.Register(&ModelSpec{
		ID: "lamda-v2", DisplayName: "LaMDA v2 (via Gemini)",
		Version: "2.0", Tier: TierLLM, Endpoint: EndpointGeminiAPI,
		GCPModelID: "gemini-1.5-pro", Region: "us-central1",
		Capabilities: CapConversation | CapTextGeneration | CapReasoning,
		MaxTokens: 8192, Parameters: "137B",
		Description: "Language Model for Dialogue Applications — evolved into Gemini",
	})
	r.Register(&ModelSpec{
		ID: "palm-2", DisplayName: "PaLM 2",
		Version: "2.0", Tier: TierLLM, Endpoint: EndpointVertexAI,
		GCPModelID: "text-bison@002", Region: "us-central1",
		Capabilities: CapTextGeneration | CapCodeGeneration | CapReasoning | CapTranslation,
		MaxTokens: 8192, Parameters: "340B",
		Description: "Pathways Language Model 2 — advanced reasoning and multilingual",
		CostPerMToken: 0.50,
	})
	r.Register(&ModelSpec{
		ID: "gemini-pro", DisplayName: "Gemini 2.5 Pro",
		Version: "2.5", Tier: TierLLM, Endpoint: EndpointGeminiAPI,
		GCPModelID: "gemini-2.5-pro", Region: "us-central1",
		Capabilities: CapTextGeneration | CapCodeGeneration | CapReasoning | CapMultimodal | CapConversation | CapImageUnderstanding,
		MaxTokens: 65536, Parameters: "~1T", IsMultimodal: true,
		Description: "Google's most capable model — native multimodal reasoning",
		CostPerMToken: 1.25,
	})
	r.Register(&ModelSpec{
		ID: "gemini-ultra", DisplayName: "Gemini Ultra",
		Version: "1.0", Tier: TierLLM, Endpoint: EndpointGeminiAPI,
		GCPModelID: "gemini-2.5-pro", Region: "us-central1",
		Capabilities: CapTextGeneration | CapCodeGeneration | CapReasoning | CapMultimodal | CapConversation | CapImageUnderstanding,
		MaxTokens: 65536, Parameters: "~1.5T", IsMultimodal: true,
		Description: "Highest capability tier of Gemini — maximum intelligence",
		CostPerMToken: 2.50,
	})
	r.Register(&ModelSpec{
		ID: "gemini-flash", DisplayName: "Gemini 2.5 Flash",
		Version: "2.5", Tier: TierLLM, Endpoint: EndpointGeminiAPI,
		GCPModelID: "gemini-2.5-flash", Region: "us-central1",
		Capabilities: CapTextGeneration | CapCodeGeneration | CapReasoning | CapMultimodal | CapConversation,
		MaxTokens: 65536, Parameters: "~400B", IsMultimodal: true,
		Description: "Speed-optimized Gemini — fastest inference with strong capability",
		CostPerMToken: 0.15,
	})
	r.Register(&ModelSpec{
		ID: "gemini-nano", DisplayName: "Gemini Nano",
		Version: "1.0", Tier: TierLLM, Endpoint: EndpointCustomDeploy,
		GCPModelID: "gemini-nano", Region: "us-central1",
		Capabilities: CapTextGeneration | CapConversation,
		MaxTokens: 4096, Parameters: "1.8B",
		Description: "On-device Gemini — runs on mobile/edge without cloud connection",
		CostPerMToken: 0,
	})

	// ── TIER 3: OPEN WEIGHTS ──
	r.Register(&ModelSpec{
		ID: "gemma-2", DisplayName: "Gemma 2",
		Version: "2.0", Tier: TierOpenWeights, Endpoint: EndpointVertexAI,
		GCPModelID: "gemma2-9b-it", Region: "us-central1",
		Capabilities: CapTextGeneration | CapConversation | CapFineTuning,
		MaxTokens: 8192, Parameters: "9B", IsOpenWeight: true,
		Description: "Lightweight open model derived from Gemini research — runs on laptop",
	})
	r.Register(&ModelSpec{
		ID: "gemma-3", DisplayName: "Gemma 3",
		Version: "3.0", Tier: TierOpenWeights, Endpoint: EndpointVertexAI,
		GCPModelID: "gemma-3-12b-it", Region: "us-central1",
		Capabilities: CapTextGeneration | CapConversation | CapMultimodal | CapFineTuning,
		MaxTokens: 8192, Parameters: "12B", IsMultimodal: true, IsOpenWeight: true,
		Description: "Gemma 3 with native multimodal vision capability",
	})
	r.Register(&ModelSpec{
		ID: "gemma-4", DisplayName: "Gemma 4",
		Version: "4.0", Tier: TierOpenWeights, Endpoint: EndpointVertexAI,
		GCPModelID: "gemma-4-27b-it", Region: "us-central1",
		Capabilities: CapTextGeneration | CapConversation | CapMultimodal | CapCodeGeneration | CapReasoning | CapFineTuning,
		MaxTokens: 32768, Parameters: "27B", IsMultimodal: true, IsOpenWeight: true,
		Description: "Most capable Gemma — thinking, agentic, multimodal open model",
	})
	r.Register(&ModelSpec{
		ID: "code-gemma", DisplayName: "CodeGemma",
		Version: "1.0", Tier: TierOpenWeights, Endpoint: EndpointVertexAI,
		GCPModelID: "codegemma-7b-it", Region: "us-central1",
		Capabilities: CapCodeGeneration | CapTextGeneration | CapFineTuning,
		MaxTokens: 8192, Parameters: "7B", IsOpenWeight: true,
		Description: "Specialized for code generation, completion, and explanation",
	})
	r.Register(&ModelSpec{
		ID: "recurrent-gemma", DisplayName: "RecurrentGemma",
		Version: "1.0", Tier: TierOpenWeights, Endpoint: EndpointVertexAI,
		GCPModelID: "recurrentgemma-2b-it", Region: "us-central1",
		Capabilities: CapTextGeneration | CapConversation | CapFineTuning,
		MaxTokens: 8192, Parameters: "2B", IsOpenWeight: true,
		Description: "Memory-efficient via Griffin recurrent architecture — edge-optimized",
	})

	// ── TIER 4: GENERATIVE MEDIA ──
	r.Register(&ModelSpec{
		ID: "imagen-3", DisplayName: "Imagen 3",
		Version: "3.0", Tier: TierGenerativeMedia, Endpoint: EndpointVertexAI,
		GCPModelID: "imagen-3.0-generate-001", Region: "us-central1",
		Capabilities: CapImageGeneration,
		MaxImageSize: 1536,
		Description: "State-of-the-art text-to-image generation — photorealistic quality",
		CostPerMToken: 20.0,
	})
	r.Register(&ModelSpec{
		ID: "imagen-edit", DisplayName: "Imagen 3 (Edit)",
		Version: "3.0", Tier: TierGenerativeMedia, Endpoint: EndpointVertexAI,
		GCPModelID: "imagen-3.0-capability-001", Region: "us-central1",
		Capabilities: CapImageGeneration | CapImageUnderstanding,
		MaxImageSize: 1536,
		Description: "Imagen editing, inpainting, and upscaling capabilities",
	})
	r.Register(&ModelSpec{
		ID: "veo-2", DisplayName: "Veo 2",
		Version: "2.0", Tier: TierGenerativeMedia, Endpoint: EndpointVertexAI,
		GCPModelID: "veo-2.0-generate-001", Region: "us-central1",
		Capabilities: CapVideoGeneration,
		Description: "Text-to-video generation — cinematic quality video creation",
		CostPerMToken: 50.0,
	})
	r.Register(&ModelSpec{
		ID: "musiclm", DisplayName: "MusicLM / Lyria",
		Version: "1.0", Tier: TierGenerativeMedia, Endpoint: EndpointCustomDeploy,
		GCPModelID: "musiclm-v1", Region: "us-central1",
		Capabilities: CapAudioGeneration,
		Description: "AI music and audio generation from text descriptions",
	})

	// ── TIER 5: VISION & SPEECH ──
	r.Register(&ModelSpec{
		ID: "vit-base", DisplayName: "Vision Transformer (ViT)",
		Version: "1.0", Tier: TierVisionSpeech, Endpoint: EndpointVisionAPI,
		GCPModelID: "vit-base-patch16-224", Region: "us-central1",
		Capabilities: CapImageUnderstanding,
		MaxImageSize: 1024,
		Description: "Standard modern AI for image classification and understanding",
	})
	r.Register(&ModelSpec{
		ID: "usm-chirp", DisplayName: "Universal Speech Model (USM/Chirp)",
		Version: "2.0", Tier: TierVisionSpeech, Endpoint: EndpointSpeechAPI,
		GCPModelID: "chirp_2", Region: "us-central1",
		Capabilities: CapSpeechRecognition | CapTranslation,
		Languages: 1000,
		Description: "1000+ language speech recognition — universal voice understanding",
	})
}
