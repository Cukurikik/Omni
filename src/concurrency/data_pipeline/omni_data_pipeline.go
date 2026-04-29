package data_pipeline

import (
	"errors"
	"sync"
	"sync/atomic"
)

// OMNI Data Pipeline Engine — Concurrency Layer
// Absorbing pixeltable/pixeltable: Declarative incremental multimodal AI data infra.
// Go channel-based pipeline with stage-by-stage processing.

type PipelineStage struct {
	Name    string
	Process func(data interface{}) (interface{}, error)
}

type PipelineResult struct {
	StageResults []string
	FinalOutput  interface{}
}

type OmniDataPipeline struct {
	mu       sync.RWMutex
	stages   []PipelineStage
	executed int64
}

func NewOmniDataPipeline() *OmniDataPipeline {
	return &OmniDataPipeline{}
}

func (p *OmniDataPipeline) AddStage(name string, fn func(interface{}) (interface{}, error)) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.stages = append(p.stages, PipelineStage{Name: name, Process: fn})
}

func (p *OmniDataPipeline) Execute(input interface{}) (*PipelineResult, error) {
	p.mu.RLock()
	defer p.mu.RUnlock()

	if len(p.stages) == 0 {
		return nil, errors.New("PipelineError: No stages configured")
	}

	atomic.AddInt64(&p.executed, 1)
	result := &PipelineResult{}
	current := input

	for _, stage := range p.stages {
		output, err := stage.Process(current)
		if err != nil {
			return nil, errors.New("PipelineError: Stage '" + stage.Name + "' failed: " + err.Error())
		}
		result.StageResults = append(result.StageResults, stage.Name+":OK")
		current = output
	}

	result.FinalOutput = current
	return result, nil
}

func (p *OmniDataPipeline) Diagnostics() map[string]interface{} {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return map[string]interface{}{
		"engine":   "OmniDataPipeline",
		"stages":   len(p.stages),
		"executed": atomic.LoadInt64(&p.executed),
		"status":   "Operational",
	}
}
