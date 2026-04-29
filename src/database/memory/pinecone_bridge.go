package memory

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"
)

type PineconeConfig struct {
	APIKey      string
	Environment string
	IndexName   string
	ProjectName string
}

type PineconeBridge struct {
	config     PineconeConfig
	httpClient *http.Client
	baseURL    string
}

func NewPineconeBridge(cfg PineconeConfig) *PineconeBridge {
	baseURL := fmt.Sprintf("https://%s-%s.svc.%s.pinecone.io", cfg.IndexName, cfg.ProjectName, cfg.Environment)
	return &PineconeBridge{
		config: cfg,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		baseURL: baseURL,
	}
}

type QueryRequest struct {
	Vector          []float32 `json:"vector"`
	TopK            int       `json:"topK"`
	IncludeMetadata bool      `json:"includeMetadata"`
}

type QueryResponse struct {
	Matches []struct {
		ID       string                 `json:"id"`
		Score    float32                `json:"score"`
		Metadata map[string]interface{} `json:"metadata"`
	} `json:"matches"`
}

func (b *PineconeBridge) Query(ctx context.Context, vector []float32, topK int) (*QueryResponse, error) {
	if len(vector) == 0 {
		return nil, errors.New("vector cannot be empty")
	}

	reqBody := QueryRequest{
		Vector:          vector,
		TopK:            topK,
		IncludeMetadata: true,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("json marshal failed: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", b.baseURL+"/query", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("request creation failed: %w", err)
	}

	req.Header.Set("Api-Key", b.config.APIKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := b.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("pinecone API returned status %d", resp.StatusCode)
	}

	var qRes QueryResponse
	if err := json.NewDecoder(resp.Body).Decode(&qRes); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &qRes, nil
}
