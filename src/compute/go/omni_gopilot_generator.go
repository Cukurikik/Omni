// OMNI Framework - Gopilot Generator
// Zero-mock implementation of a tiny code-generation LLM API client trained on Go.

package generator

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type GopilotRequest struct {
	Context     string  `json:"context"`
	MaxTokens   int     `json:"max_tokens"`
	Temperature float64 `json:"temperature"`
}

type GopilotResponse struct {
	Completion string `json:"completion"`
	LatencyMs  int64  `json:"latency_ms"`
	Error      string `json:"error,omitempty"`
}

type OmniGopilotClient struct {
	EndpointURL string
	HTTPClient  *http.Client
}

func NewOmniGopilotClient(endpoint string) *OmniGopilotClient {
	return &OmniGopilotClient{
		EndpointURL: endpoint,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// GenerateCode sends a snippet context to the Gopilot inference server and returns the autocompletion
func (c *OmniGopilotClient) GenerateCode(context string) (*GopilotResponse, error) {
	reqData := GopilotRequest{
		Context:     context,
		MaxTokens:   128,
		Temperature: 0.2, // Low temp for code precision
	}

	bodyBytes, err := json.Marshal(reqData)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal gopilot request: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, c.EndpointURL, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	start := time.Now()
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("gopilot inference request failed: %w", err)
	}
	defer resp.Body.Close()

	var result GopilotResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode gopilot response: %w", err)
	}

	result.LatencyMs = time.Since(start).Milliseconds()
	return &result, nil
}
