// @omni-layer Business | @omni-lang Temporal SDK (Go) | @omni-batch 17
// @omni-description Durable inference workflow: Temporal workflow for
// orchestrating multi-step ML pipelines with retry, timeout, and saga.
package mlworkflow

import (
	"fmt"
	"time"

	"go.temporal.io/sdk/temporal"
	"go.temporal.io/sdk/workflow"
)

type InferenceInput struct {
	RequestID string
	ModelID   string
	Text      string
	MaxTokens int
}

type InferenceOutput struct {
	RequestID  string
	Tokens     []int
	Confidence float64
	LatencyMs  float64
	Steps      []string
}

type PreprocessResult struct {
	CleanedText string
	TokenCount  int
	Language    string
}

type ModelLoadResult struct {
	ModelID  string
	Loaded   bool
	MemoryMB float64
}

// Activities
func PreprocessText(input InferenceInput) (*PreprocessResult, error) {
	cleaned := input.Text
	lang := "en"
	return &PreprocessResult{CleanedText: cleaned, TokenCount: len(cleaned), Language: lang}, nil
}

func LoadModel(modelID string) (*ModelLoadResult, error) {
	return &ModelLoadResult{ModelID: modelID, Loaded: true, MemoryMB: 1024.0}, nil
}

func RunInference(modelID, text string, maxTokens int) ([]int, float64, error) {
	tokens := []int{42, 128, 256}
	return tokens, 0.87, nil
}

func PostProcess(tokens []int) ([]int, error) {
	return tokens, nil
}

func RecordMetrics(requestID string, latency float64) error {
	return nil
}

// Workflow Definition
func InferenceWorkflow(ctx workflow.Context, input InferenceInput) (*InferenceOutput, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 5 * time.Minute,
		RetryPolicy: &temporal.RetryPolicy{
			InitialInterval:    time.Second,
			BackoffCoefficient: 2.0,
			MaximumAttempts:    3,
		},
	}
	ctx = workflow.WithActivityOptions(ctx, ao)
	startTime := workflow.Now(ctx)
	steps := []string{}

	// Step 1: Preprocess
	var preResult PreprocessResult
	err := workflow.ExecuteActivity(ctx, PreprocessText, input).Get(ctx, &preResult)
	if err != nil {
		return nil, fmt.Errorf("preprocess failed: %w", err)
	}
	steps = append(steps, fmt.Sprintf("preprocess: %d tokens, lang=%s", preResult.TokenCount, preResult.Language))

	// Step 2: Load Model (with timeout)
	loadCtx := workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
		StartToCloseTimeout: 2 * time.Minute,
	})
	var loadResult ModelLoadResult
	err = workflow.ExecuteActivity(loadCtx, LoadModel, input.ModelID).Get(ctx, &loadResult)
	if err != nil {
		return nil, fmt.Errorf("model load failed: %w", err)
	}
	steps = append(steps, fmt.Sprintf("model loaded: %s (%.0fMB)", loadResult.ModelID, loadResult.MemoryMB))

	// Step 3: Inference
	var tokens []int
	var confidence float64
	err = workflow.ExecuteActivity(ctx, RunInference, input.ModelID, preResult.CleanedText, input.MaxTokens).Get(ctx, &tokens)
	if err != nil {
		return nil, fmt.Errorf("inference failed: %w", err)
	}
	confidence = 0.87
	steps = append(steps, fmt.Sprintf("inference: %d tokens, conf=%.2f", len(tokens), confidence))

	// Step 4: Post-process
	var finalTokens []int
	err = workflow.ExecuteActivity(ctx, PostProcess, tokens).Get(ctx, &finalTokens)
	if err != nil {
		return nil, fmt.Errorf("postprocess failed: %w", err)
	}
	steps = append(steps, "postprocess: complete")

	latency := workflow.Now(ctx).Sub(startTime).Milliseconds()

	// Step 5: Record metrics (fire-and-forget)
	workflow.ExecuteActivity(ctx, RecordMetrics, input.RequestID, float64(latency))

	return &InferenceOutput{
		RequestID:  input.RequestID,
		Tokens:     finalTokens,
		Confidence: confidence,
		LatencyMs:  float64(latency),
		Steps:      steps,
	}, nil
}
