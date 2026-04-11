package foundation

import (
	"fmt"
	"log"
	"math"
)

// ==========================================
// 🏗️ OMNI AI — TRANSFORMER BASE MODEL
// ==========================================
// Implements the core Transformer architecture concepts from
// "Attention Is All You Need" (Vaswani et al., 2017).
//
// This serves as the foundational building block for ALL modern
// AI models (GPT, Gemini, BERT, T5, PaLM, Gemma, etc.)
//
// In OMNI, this is the architectural reference — actual inference
// routes through GCP Vertex AI / Gemini API endpoints.

// TransformerConfig holds architecture hyperparameters
type TransformerConfig struct {
	ModelDim       int     // d_model: dimensionality of embeddings (default: 512)
	NumHeads       int     // h: number of attention heads (default: 8)
	NumLayers      int     // N: number of encoder/decoder layers (default: 6)
	FFNDim         int     // d_ff: feed-forward network dimension (default: 2048)
	VocabSize      int     // V: vocabulary size (default: 32000)
	MaxSeqLength   int     // Maximum sequence length (default: 512)
	DropoutRate    float64 // Dropout probability (default: 0.1)
	LearningRate   float64 // Initial learning rate
	WarmupSteps    int     // Warmup steps for learning rate scheduler
	AttentionType  string  // "self", "cross", "multi-query", "grouped-query"
}

// DefaultTransformerConfig returns the original paper's configuration
func DefaultTransformerConfig() *TransformerConfig {
	return &TransformerConfig{
		ModelDim:      512,
		NumHeads:      8,
		NumLayers:     6,
		FFNDim:        2048,
		VocabSize:     32000,
		MaxSeqLength:  512,
		DropoutRate:   0.1,
		LearningRate:  0.0001,
		WarmupSteps:   4000,
		AttentionType: "self",
	}
}

// TransformerBase represents the base Transformer model
type TransformerBase struct {
	Config     *TransformerConfig
	Name       string
	Parameters int64
}

// NewTransformerBase creates a new Transformer model instance
func NewTransformerBase(config *TransformerConfig) *TransformerBase {
	params := estimateParameters(config)
	model := &TransformerBase{
		Config:     config,
		Name:       "Transformer-Base",
		Parameters: params,
	}

	log.Printf("🏗️ [TRANSFORMER] Initialized: d_model=%d, heads=%d, layers=%d, params=%s",
		config.ModelDim, config.NumHeads, config.NumLayers, formatParams(params))

	return model
}

// ScaledDotProductAttention computes attention weights
// Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) × V
func (t *TransformerBase) ScaledDotProductAttention(queryDim, keyDim int) float64 {
	dk := float64(t.Config.ModelDim / t.Config.NumHeads)
	scaleFactor := 1.0 / math.Sqrt(dk)

	log.Printf("🧮 [ATTENTION] Scale factor: 1/√%d = %.6f", int(dk), scaleFactor)
	return scaleFactor
}

// MultiHeadAttention splits dimensions across attention heads
// MultiHead(Q,K,V) = Concat(head_1,...,head_h) × W^O
func (t *TransformerBase) MultiHeadAttention() map[string]int {
	headDim := t.Config.ModelDim / t.Config.NumHeads
	return map[string]int{
		"num_heads":       t.Config.NumHeads,
		"head_dim":        headDim,
		"total_dim":       t.Config.ModelDim,
		"attention_params": 4 * t.Config.ModelDim * t.Config.ModelDim, // Q,K,V,O projections
	}
}

// PositionalEncoding computes sinusoidal position encodings
// PE(pos,2i) = sin(pos/10000^(2i/d_model))
// PE(pos,2i+1) = cos(pos/10000^(2i/d_model))
func (t *TransformerBase) PositionalEncoding(position, dimension int) float64 {
	angle := float64(position) / math.Pow(10000.0, float64(2*(dimension/2))/float64(t.Config.ModelDim))
	if dimension%2 == 0 {
		return math.Sin(angle)
	}
	return math.Cos(angle)
}

// FeedForwardNetwork describes the FFN sublayer
// FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
func (t *TransformerBase) FeedForwardNetwork() map[string]int {
	return map[string]int{
		"input_dim":  t.Config.ModelDim,
		"hidden_dim": t.Config.FFNDim,
		"output_dim": t.Config.ModelDim,
		"params":     2*t.Config.ModelDim*t.Config.FFNDim + t.Config.ModelDim + t.Config.FFNDim,
	}
}

// LayerNormalization describes pre/post layer norm
func (t *TransformerBase) LayerNormalization() map[string]int {
	return map[string]int{
		"gamma_params": t.Config.ModelDim,
		"beta_params":  t.Config.ModelDim,
		"total":        2 * t.Config.ModelDim,
	}
}

// GetArchitectureSummary returns full model architecture details
func (t *TransformerBase) GetArchitectureSummary() map[string]interface{} {
	return map[string]interface{}{
		"name":       t.Name,
		"params":     t.Parameters,
		"params_str": formatParams(t.Parameters),
		"config":     t.Config,
		"attention":  t.MultiHeadAttention(),
		"ffn":        t.FeedForwardNetwork(),
		"layer_norm": t.LayerNormalization(),
		"layers":     t.Config.NumLayers,
		"vocab_size": t.Config.VocabSize,
		"paper":      "Vaswani et al., 2017 — Attention Is All You Need",
	}
}

// ── Helper Functions ──

func estimateParameters(config *TransformerConfig) int64 {
	// Embedding params
	embedding := int64(config.VocabSize * config.ModelDim)

	// Per-layer params: 4 attention projections + 2 FFN layers + 2 layer norms
	perLayer := int64(4*config.ModelDim*config.ModelDim +
		2*config.ModelDim*config.FFNDim +
		4*config.ModelDim)

	// Total: embeddings + (layers × per-layer) + final layer norm
	total := embedding + int64(config.NumLayers)*perLayer + int64(2*config.ModelDim)
	return total
}

func formatParams(params int64) string {
	switch {
	case params >= 1_000_000_000:
		return fmt.Sprintf("%.1fB", float64(params)/1e9)
	case params >= 1_000_000:
		return fmt.Sprintf("%.1fM", float64(params)/1e6)
	case params >= 1_000:
		return fmt.Sprintf("%.1fK", float64(params)/1e3)
	default:
		return fmt.Sprintf("%d", params)
	}
}
