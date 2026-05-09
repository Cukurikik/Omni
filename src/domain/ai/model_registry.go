//=============================================================================
// OMNI DOMAIN LAYER — MODEL REGISTRY (GO)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Go memory registry for managing active models available in the
//              Compute Layer. Allows API routing to correctly available models.
//=============================================================================

package domain

import (
	"errors"
	"sync"
)

type AIModel struct {
	ID          string
	Type        string // e.g., "transformer", "asr", "vision"
	Parameters  int64
	IsLoaded    bool
	ComputeNode string
}

type ModelRegistry struct {
	models map[string]*AIModel
	mu     sync.RWMutex
}

func NewModelRegistry() *ModelRegistry {
	return &ModelRegistry{
		models: make(map[string]*AIModel),
	}
}

func (r *ModelRegistry) RegisterModel(model *AIModel) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.models[model.ID] = model
}

func (r *ModelRegistry) GetModel(id string) (*AIModel, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if model, exists := r.models[id]; exists {
		if !model.IsLoaded {
			return nil, errors.New("model registered but not loaded into memory")
		}
		return model, nil
	}

	return nil, errors.New("model not found in registry")
}

func (r *ModelRegistry) ListActiveModels() []AIModel {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var active []AIModel
	for _, m := range r.models {
		if m.IsLoaded {
			active = append(active, *m)
		}
	}
	return active
}
