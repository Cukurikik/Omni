// OMNI FRAMEWORK: BATCH 1 SEMESTER 14
// ENGINE: OMNI COG ML CONTAINER ENGINE
// DOMAIN: COMPUTE / INFRASTRUCTURE (GO)
// ZERO MOCK - PRODUCTION READY
// ==========================================

package cog

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
	"sync"
	"sync/atomic"
	"time"
)

// CogError defines custom error structures for the ML container engine.
type CogError struct {
	Code    string
	Message string
	Err     error
}

func (e *CogError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("CogError[%s]: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("CogError[%s]: %s", e.Code, e.Message)
}

// CogResult is the monadic error return for container operations.
type CogResult[T any] struct {
	Value T
	Err   error
}

// ModelDefinition represents the declarative environment for an ML model.
type ModelDefinition struct {
	Build struct {
		GPU          bool     `json:"gpu"`
		PythonVersion string   `json:"python_version"`
		SystemPkgs   []string `json:"system_packages"`
		PythonPkgs   []string `json:"python_packages"`
		RunCommands  []string `json:"run"`
	} `json:"build"`
	Predict string `json:"predict"` // Path to prediction script
}

// OmniCogEngine orchestrates lightweight ML container boundaries.
type OmniCogEngine struct {
	mu            sync.RWMutex
	activeModels  map[string]ModelDefinition
	containerIDs  map[string]string // maps model name to docker/OCI container ID
	
	// Metrics
	buildsTriggered atomic.Int64
	buildsFailed    atomic.Int64
	activeTasks     atomic.Int64
}

// NewOmniCogEngine initializes the containerization manager.
func NewOmniCogEngine() *OmniCogEngine {
	return &OmniCogEngine{
		activeModels: make(map[string]ModelDefinition),
		containerIDs: make(map[string]string),
	}
}

// RegisterModel registers an ML model boundary.
func (e *OmniCogEngine) RegisterModel(name string, def ModelDefinition) CogResult[bool] {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.activeModels[name]; exists {
		return CogResult[bool]{Err: &CogError{Code: "MODEL_EXISTS", Message: fmt.Sprintf("Model %s is already registered", name)}}
	}

	e.activeModels[name] = def
	return CogResult[bool]{Value: true}
}

// Build triggers the actual building of an OCI container for the model via Docker CLI.
func (e *OmniCogEngine) Build(ctx context.Context, name string) CogResult[string] {
	e.mu.RLock()
	def, exists := e.activeModels[name]
	e.mu.RUnlock()

	if !exists {
		return CogResult[string]{Err: &CogError{Code: "NOT_FOUND", Message: "Model not registered"}}
	}

	e.buildsTriggered.Add(1)

	// In a real environment, this generates a Dockerfile and builds it.
	// We generate the Dockerfile in memory to demonstrate zero-mock architecture.
	var dockerfile bytes.Buffer
	if def.Build.GPU {
		dockerfile.WriteString("FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04\n")
	} else {
		dockerfile.WriteString("FROM ubuntu:22.04\n")
	}

	dockerfile.WriteString("ENV DEBIAN_FRONTEND=noninteractive\n")
	dockerfile.WriteString("RUN apt-get update && apt-get install -y python3 python3-pip ")
	for _, pkg := range def.Build.SystemPkgs {
		dockerfile.WriteString(pkg + " ")
	}
	dockerfile.WriteString("&& rm -rf /var/lib/apt/lists/*\n")

	for _, cmd := range def.Build.RunCommands {
		dockerfile.WriteString(fmt.Sprintf("RUN %s\n", cmd))
	}

	if len(def.Build.PythonPkgs) > 0 {
		dockerfile.WriteString("RUN pip3 install ")
		for _, pkg := range def.Build.PythonPkgs {
			dockerfile.WriteString(pkg + " ")
		}
		dockerfile.WriteString("\n")
	}

	dockerfile.WriteString(fmt.Sprintf("COPY . /src\nWORKDIR /src\nCMD [\"python3\", \"%s\"]\n", def.Predict))

	// Execute Docker build via CLI (stdin)
	cmd := exec.CommandContext(ctx, "docker", "build", "-q", "-t", fmt.Sprintf("omni-cog-%s", name), "-")
	cmd.Stdin = &dockerfile

	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	if err := cmd.Run(); err != nil {
		e.buildsFailed.Add(1)
		return CogResult[string]{Err: &CogError{Code: "BUILD_FAILED", Message: out.String(), Err: err}}
	}

	return CogResult[string]{Value: out.String()}
}

// Predict sends inference requests to the active ML container.
func (e *OmniCogEngine) Predict(ctx context.Context, name string, input map[string]interface{}) CogResult[map[string]interface{}] {
	e.mu.RLock()
	_, exists := e.activeModels[name]
	e.mu.RUnlock()

	if !exists {
		return CogResult[map[string]interface{}]{Err: &CogError{Code: "NOT_FOUND", Message: "Model not registered"}}
	}

	e.activeTasks.Add(1)
	defer e.activeTasks.Add(-1)

	payload, err := json.Marshal(input)
	if err != nil {
		return CogResult[map[string]interface{}]{Err: &CogError{Code: "INVALID_INPUT", Message: "Failed to serialize input", Err: err}}
	}

	// We pass the payload into the docker container running the model
	cmd := exec.CommandContext(ctx, "docker", "run", "--rm", "-i", fmt.Sprintf("omni-cog-%s", name))
	cmd.Stdin = bytes.NewReader(payload)

	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return CogResult[map[string]interface{}]{Err: &CogError{Code: "INFERENCE_FAILED", Message: stderr.String(), Err: err}}
	}

	var result map[string]interface{}
	if err := json.Unmarshal(out.Bytes(), &result); err != nil {
		return CogResult[map[string]interface{}]{Err: &CogError{Code: "INVALID_OUTPUT", Message: "Failed to parse inference output", Err: err}}
	}

	return CogResult[map[string]interface{}]{Value: result}
}

// Diagnostics returns current state metrics.
func (e *OmniCogEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":           "OmniCogEngine",
		"version":          "1.0.0-production",
		"active_models":    len(e.activeModels),
		"builds_triggered": e.buildsTriggered.Load(),
		"builds_failed":    e.buildsFailed.Load(),
		"active_tasks":     e.activeTasks.Load(),
		"timestamp":        time.Now().Unix(),
		"status":           "operational",
	}
}
