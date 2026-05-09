// omni_model_registry.go — Distributed Model Registry Service
// Inspired by: MLflow + OMNI deployment architecture
// Layer: Network / Go
//
// gRPC-compatible model versioning, serving, and lifecycle management.
// Tracks model artifacts, metrics, and deployment status.

package registry

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"time"
)

// ModelStage represents the lifecycle stage of a model version.
type ModelStage string

const (
	StageNone       ModelStage = "None"
	StageStaging    ModelStage = "Staging"
	StageProduction ModelStage = "Production"
	StageArchived   ModelStage = "Archived"
)

// ModelFormat describes the serialization format.
type ModelFormat string

const (
	FormatONNX        ModelFormat = "onnx"
	FormatTorchScript ModelFormat = "torchscript"
	FormatSafeTensors ModelFormat = "safetensors"
	FormatTFLite      ModelFormat = "tflite"
	FormatOpenVINO    ModelFormat = "openvino"
)

// ModelMetrics stores evaluation results.
type ModelMetrics struct {
	Accuracy    float64            `json:"accuracy,omitempty"`
	Loss        float64            `json:"loss,omitempty"`
	Latency95ms float64            `json:"latency_p95_ms,omitempty"`
	Throughput  float64            `json:"throughput_rps,omitempty"`
	Custom      map[string]float64 `json:"custom,omitempty"`
}

// ModelVersion represents a specific version of a registered model.
type ModelVersion struct {
	Version      int               `json:"version"`
	Stage        ModelStage        `json:"stage"`
	Format       ModelFormat       `json:"format"`
	ArtifactPath string            `json:"artifact_path"`
	ArtifactHash string            `json:"artifact_hash"`
	ArtifactSize int64             `json:"artifact_size_bytes"`
	Metrics      ModelMetrics      `json:"metrics"`
	Parameters   map[string]string `json:"parameters"`
	Tags         map[string]string `json:"tags"`
	CreatedAt    time.Time         `json:"created_at"`
	UpdatedAt    time.Time         `json:"updated_at"`
	Description  string            `json:"description"`
}

// RegisteredModel is a named model with multiple versions.
type RegisteredModel struct {
	Name          string                `json:"name"`
	Description   string                `json:"description"`
	Tags          map[string]string     `json:"tags"`
	Versions      map[int]*ModelVersion `json:"versions"`
	LatestVersion int                   `json:"latest_version"`
	CreatedAt     time.Time             `json:"created_at"`
	UpdatedAt     time.Time             `json:"updated_at"`
}

// OmniModelRegistry manages the full model lifecycle.
type OmniModelRegistry struct {
	mu          sync.RWMutex
	models      map[string]*RegisteredModel
	storagePath string
}

// NewModelRegistry creates a new registry with the given storage root.
func NewModelRegistry(storagePath string) (*OmniModelRegistry, error) {
	if err := os.MkdirAll(storagePath, 0755); err != nil {
		return nil, fmt.Errorf("failed to create storage directory: %w", err)
	}
	registry := &OmniModelRegistry{
		models:      make(map[string]*RegisteredModel),
		storagePath: storagePath,
	}

	// Load existing registry state
	if err := registry.loadState(); err != nil {
		// First run — no existing state
		_ = err
	}

	return registry, nil
}

// CreateModel registers a new named model.
func (r *OmniModelRegistry) CreateModel(name, description string, tags map[string]string) (*RegisteredModel, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.models[name]; exists {
		return nil, fmt.Errorf("model %q already exists", name)
	}

	now := time.Now().UTC()
	model := &RegisteredModel{
		Name:          name,
		Description:   description,
		Tags:          tags,
		Versions:      make(map[int]*ModelVersion),
		LatestVersion: 0,
		CreatedAt:     now,
		UpdatedAt:     now,
	}

	r.models[name] = model
	r.persistState()
	return model, nil
}

// RegisterVersion adds a new version of a model from a file path.
func (r *OmniModelRegistry) RegisterVersion(
	modelName string,
	artifactPath string,
	format ModelFormat,
	metrics ModelMetrics,
	params map[string]string,
	description string,
) (*ModelVersion, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	model, exists := r.models[modelName]
	if !exists {
		return nil, fmt.Errorf("model %q not found", modelName)
	}

	// Compute artifact hash
	hash, size, err := computeFileHash(artifactPath)
	if err != nil {
		return nil, fmt.Errorf("failed to hash artifact: %w", err)
	}

	// Copy artifact to managed storage
	version := model.LatestVersion + 1
	destDir := filepath.Join(r.storagePath, modelName, fmt.Sprintf("v%d", version))
	if err := os.MkdirAll(destDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create version directory: %w", err)
	}

	destPath := filepath.Join(destDir, filepath.Base(artifactPath))
	if err := copyFile(artifactPath, destPath); err != nil {
		return nil, fmt.Errorf("failed to copy artifact: %w", err)
	}

	now := time.Now().UTC()
	mv := &ModelVersion{
		Version:      version,
		Stage:        StageNone,
		Format:       format,
		ArtifactPath: destPath,
		ArtifactHash: hash,
		ArtifactSize: size,
		Metrics:      metrics,
		Parameters:   params,
		Tags:         make(map[string]string),
		CreatedAt:    now,
		UpdatedAt:    now,
		Description:  description,
	}

	model.Versions[version] = mv
	model.LatestVersion = version
	model.UpdatedAt = now

	r.persistState()
	return mv, nil
}

// TransitionStage moves a model version to a new lifecycle stage.
func (r *OmniModelRegistry) TransitionStage(modelName string, version int, newStage ModelStage) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	model, exists := r.models[modelName]
	if !exists {
		return fmt.Errorf("model %q not found", modelName)
	}

	mv, exists := model.Versions[version]
	if !exists {
		return fmt.Errorf("version %d not found for model %q", version, modelName)
	}

	// If promoting to Production, demote existing production version
	if newStage == StageProduction {
		for _, v := range model.Versions {
			if v.Stage == StageProduction && v.Version != version {
				v.Stage = StageArchived
				v.UpdatedAt = time.Now().UTC()
			}
		}
	}

	mv.Stage = newStage
	mv.UpdatedAt = time.Now().UTC()
	model.UpdatedAt = mv.UpdatedAt

	r.persistState()
	return nil
}

// GetProductionVersion returns the current production version.
func (r *OmniModelRegistry) GetProductionVersion(modelName string) (*ModelVersion, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	model, exists := r.models[modelName]
	if !exists {
		return nil, fmt.Errorf("model %q not found", modelName)
	}

	for _, v := range model.Versions {
		if v.Stage == StageProduction {
			return v, nil
		}
	}

	return nil, fmt.Errorf("no production version for model %q", modelName)
}

// ListModels returns all registered models sorted by name.
func (r *OmniModelRegistry) ListModels() []*RegisteredModel {
	r.mu.RLock()
	defer r.mu.RUnlock()

	models := make([]*RegisteredModel, 0, len(r.models))
	for _, m := range r.models {
		models = append(models, m)
	}
	sort.Slice(models, func(i, j int) bool {
		return models[i].Name < models[j].Name
	})
	return models
}

// CompareVersions returns a diff of metrics between two versions.
func (r *OmniModelRegistry) CompareVersions(
	modelName string, v1, v2 int,
) (map[string]float64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	model, exists := r.models[modelName]
	if !exists {
		return nil, fmt.Errorf("model %q not found", modelName)
	}

	mv1, ok1 := model.Versions[v1]
	mv2, ok2 := model.Versions[v2]
	if !ok1 || !ok2 {
		return nil, fmt.Errorf("version(s) not found")
	}

	diff := map[string]float64{
		"accuracy_delta":   mv2.Metrics.Accuracy - mv1.Metrics.Accuracy,
		"loss_delta":       mv2.Metrics.Loss - mv1.Metrics.Loss,
		"latency_delta_ms": mv2.Metrics.Latency95ms - mv1.Metrics.Latency95ms,
		"throughput_delta": mv2.Metrics.Throughput - mv1.Metrics.Throughput,
	}
	return diff, nil
}

func (r *OmniModelRegistry) persistState() {
	statePath := filepath.Join(r.storagePath, "registry_state.json")
	data, err := json.MarshalIndent(r.models, "", "  ")
	if err != nil {
		return
	}
	os.WriteFile(statePath, data, 0644)
}

func (r *OmniModelRegistry) loadState() error {
	statePath := filepath.Join(r.storagePath, "registry_state.json")
	data, err := os.ReadFile(statePath)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, &r.models)
}

func computeFileHash(path string) (string, int64, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", 0, err
	}
	defer f.Close()

	hasher := sha256.New()
	size, err := io.Copy(hasher, f)
	if err != nil {
		return "", 0, err
	}
	return hex.EncodeToString(hasher.Sum(nil)), size, nil
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, in)
	return err
}
