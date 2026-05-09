// @omni-layer Concurrency | @omni-source PaddlePaddle/PALM | @omni-lang Go
// @omni-description Distributed multi-task training coordinator with task priority
// queue and dynamic resource allocation across workers.
package palm

import (
	"math"
	"sync"
	"time"
)

type TaskConfig struct {
	Name     string
	Weight   float64
	Priority int
	NClasses int
}

type TrainingState struct {
	mu         sync.RWMutex
	tasks      []TaskConfig
	taskLosses map[string][]float64
	globalStep int64
	startTime  time.Time
	nWorkers   int
}

func NewTrainingState(tasks []TaskConfig, nWorkers int) *TrainingState {
	return &TrainingState{
		tasks: tasks, taskLosses: make(map[string][]float64),
		globalStep: 0, startTime: time.Now(), nWorkers: nWorkers,
	}
}

func (ts *TrainingState) RecordLoss(taskName string, loss float64) {
	ts.mu.Lock()
	defer ts.mu.Unlock()
	ts.taskLosses[taskName] = append(ts.taskLosses[taskName], loss)
	ts.globalStep++
}

func (ts *TrainingState) WeightedLoss() float64 {
	ts.mu.RLock()
	defer ts.mu.RUnlock()
	total := 0.0
	for _, task := range ts.tasks {
		losses := ts.taskLosses[task.Name]
		if len(losses) > 0 {
			total += task.Weight * losses[len(losses)-1]
		}
	}
	return total
}

func (ts *TrainingState) GetReport() map[string]interface{} {
	ts.mu.RLock()
	defer ts.mu.RUnlock()
	report := map[string]interface{}{
		"global_step":   ts.globalStep,
		"elapsed_sec":   time.Since(ts.startTime).Seconds(),
		"weighted_loss": ts.WeightedLoss(),
		"steps_per_sec": float64(ts.globalStep) / math.Max(time.Since(ts.startTime).Seconds(), 0.001),
	}
	taskStats := make(map[string]interface{})
	for _, task := range ts.tasks {
		losses := ts.taskLosses[task.Name]
		if len(losses) > 0 {
			taskStats[task.Name] = map[string]interface{}{
				"latest_loss": losses[len(losses)-1],
				"n_updates":   len(losses),
			}
		}
	}
	report["tasks"] = taskStats
	return report
}
