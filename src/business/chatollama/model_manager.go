package chatollama

import (
	"time"
	"fmt"
	"encoding/json"
	"net/http"
)

// OMNI CHATOLLAMA: Model Manager
// Go domain logic for interacting with the local Ollama daemon to pull, list, and manage LLMs.
// Source: ollama-webui

type ModelManagerError struct {
	Code    string
	Message string
}

func (e *ModelManagerError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

type ModelInfo struct {
	Name       string `json:"name"`
	ModifiedAt string `json:"modified_at"`
	Size       int64  `json:"size"`
}

type ModelManager struct {
	ollamaEndpoint string
	client         *http.Client
}

func NewModelManager(endpoint string) *ModelManager {
	return &ModelManager{
		ollamaEndpoint: endpoint,
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// ListModels queries the Ollama daemon for available models
func (m *ModelManager) ListModels() ([]ModelInfo, error) {
	resp, err := m.client.Get(fmt.Sprintf("%s/api/tags", m.ollamaEndpoint))
	if err != nil {
		return nil, &ModelManagerError{Code: "CONN_ERR", Message: "Failed to connect to Ollama daemon"}
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, &ModelManagerError{Code: "API_ERR", Message: fmt.Sprintf("Ollama returned status: %d", resp.StatusCode)}
	}

	var result struct {
		Models []ModelInfo `json:"models"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, &ModelManagerError{Code: "PARSE_ERR", Message: "Failed to parse Ollama response"}
	}

	return result.Models, nil
}

// CheckIfModelExists verifies if a model is downloaded
func (m *ModelManager) CheckIfModelExists(modelName string) (bool, error) {
	models, err := m.ListModels()
	if err != nil {
		return false, err
	}

	for _, mod := range models {
		if mod.Name == modelName || mod.Name == modelName+":latest" {
			return true, nil
		}
	}
	return false, nil
}
