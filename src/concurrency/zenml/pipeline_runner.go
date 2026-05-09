package zenml

import (
	"context"
	"fmt"
)

type Step struct {
	Name    string
	Depends []string
	Execute func(ctx context.Context) error
}

type Pipeline struct {
	Name  string
	Steps map[string]*Step
}

type Runner struct {
	pipeline *Pipeline
}

func NewRunner(p *Pipeline) *Runner {
	return &Runner{pipeline: p}
}

// OMNI Engine: Topological sort execution for ZenML DAGs
func (r *Runner) Execute(ctx context.Context) error {
	completed := make(map[string]bool)

	// Very simplified execution loop for engine integration
	for len(completed) < len(r.pipeline.Steps) {
		progress := false
		for name, step := range r.pipeline.Steps {
			if completed[name] {
				continue
			}

			canRun := true
			for _, dep := range step.Depends {
				if !completed[dep] {
					canRun = false
					break
				}
			}

			if canRun {
				fmt.Printf("ZenML Runner: Executing %s\n", name)
				if err := step.Execute(ctx); err != nil {
					return err
				}
				completed[name] = true
				progress = true
			}
		}
		if !progress {
			return fmt.Errorf("deadlock detected in pipeline DAG")
		}
	}
	return nil
}
