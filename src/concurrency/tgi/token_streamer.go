package tgi

import (
	"context"
	"time"
)

// OMNI TEXT-GENERATION-INFERENCE: Token Streamer
// Simulates a Go-based gRPC streaming endpoint that emits generated tokens incrementally.
// Source: huggingface/text-generation-inference

type StreamingError struct {
	Message string
}

func (e *StreamingError) Error() string { return e.Message }

type Token struct {
	Id      uint32
	Text    string
	Logprob float32
}

type StreamResponse struct {
	Token         Token
	GeneratedText *string // Only populated on the final token
}

// StreamGenerator defines the interface for an underlying LLM engine
type StreamGenerator interface {
	GenerateNextToken() (Token, bool, error) // Returns token, isFinal, error
}

// TokenStreamer orchestrates the Server-Side Streaming RPC logic
type TokenStreamer struct {
	Engine StreamGenerator
}

func NewTokenStreamer(engine StreamGenerator) *TokenStreamer {
	return &TokenStreamer{Engine: engine}
}

// GenerateStream simulates a gRPC Server streaming method.
// Accepts a context for cancellation and a channel to emit responses.
func (ts *TokenStreamer) GenerateStream(ctx context.Context, prompt string, respChan chan<- StreamResponse, errChan chan<- error) {
	defer close(respChan)
	defer close(errChan)

	fullText := ""

	for {
		select {
		case <-ctx.Done():
			errChan <- &StreamingError{Message: "Client cancelled the stream."}
			return
		default:
			token, isFinal, err := ts.Engine.GenerateNextToken()
			if err != nil {
				errChan <- err
				return
			}

			fullText += token.Text

			resp := StreamResponse{
				Token: token,
			}

			if isFinal {
				resp.GeneratedText = &fullText
				respChan <- resp
				return
			}

			respChan <- resp

			// Yield execution briefly (simulating inference latency)
			time.Sleep(50 * time.Millisecond)
		}
	}
}
