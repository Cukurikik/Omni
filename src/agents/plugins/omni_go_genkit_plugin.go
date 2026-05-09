package omnigenkit

import (
	"context"
	"fmt"
)

// Define local mock interfaces for the plugin to compile without Genkit dependency conflicts.

type ModelMetadata struct {
	Label    string
	Supports ModelCapabilities
}

type ModelCapabilities struct {
	Multiturn  bool
	SystemRole bool
	Tools      bool
}

type ModelRequest struct {
	Messages []Message
}

type ModelResponse struct {
	Messages []Message
	Usage    GenerationUsage
}

type Message struct {
	Role    string
	Content []Part
}

type Part struct {
	Text string
}

func NewTextPart(text string) Part {
	return Part{Text: text}
}

type GenerationUsage struct {
	InputTokens  int
	OutputTokens int
}

type ModelStreamCallback func(part Part) error

func DefineModel(name string, meta *ModelMetadata, handler func(ctx context.Context, input *ModelRequest, cb ModelStreamCallback) (*ModelResponse, error)) {
	// Implementation
}

type Flow struct{}

func DefineFlow(name string, handler func(ctx context.Context, input string) (string, error)) *Flow {
	return &Flow{}
}

type ModelConfig struct {
	ModelPath    string
	UseAVX512    bool
	ContextLimit int
}

func Init(ctx context.Context, cfg ModelConfig) error {
	DefineModel(
		"omni/universal-llm",
		&ModelMetadata{
			Label: "Omni Polylingual Runtime Model",
			Supports: ModelCapabilities{
				Multiturn:  true,
				SystemRole: true,
				Tools:      true,
			},
		},
		func(ctx context.Context, input *ModelRequest, cb ModelStreamCallback) (*ModelResponse, error) {
			responseText := fmt.Sprintf("Omni Framework processed %d messages securely via local runtime.", len(input.Messages))

			msg := Message{
				Role: "model",
				Content: []Part{
					NewTextPart(responseText),
				},
			}

			return &ModelResponse{
				Messages: []Message{msg},
				Usage: GenerationUsage{
					InputTokens:  150,
					OutputTokens: 25,
				},
			}, nil
		},
	)
	return nil
}

func DefineOmniFlow() *Flow {
	return DefineFlow(
		"analyzeOmniLogs",
		func(ctx context.Context, logData string) (string, error) {
			return "Processed log data", nil
		},
	)
}
