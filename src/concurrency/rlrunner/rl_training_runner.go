// @omni-layer Concurrency | @omni-source lucidrains/improving-transformers-world-model-for-rl | @omni-lang Go
// @omni-description RL training runner: concurrent multi-environment RL
// training with parallel rollout collection and value estimation.
package rlrunner

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type Transition struct {
	State     []float64
	Action    int
	Reward    float64
	NextState []float64
	Done      bool
	Value     float64
}

type EpisodeResult struct {
	EnvID          int
	TotalReward    float64
	Steps          int
	AvgValue       float64
	DiscountReturn float64
}

type RLTrainingRunner struct {
	mu       sync.Mutex
	workers  int
	nEnvs    int
	gamma    float64
	dState   int
	nActions int
	episodes int
}

func NewRLTrainingRunner(workers, nEnvs int, gamma float64, dState, nActions int) *RLTrainingRunner {
	return &RLTrainingRunner{workers: workers, nEnvs: nEnvs, gamma: gamma, dState: dState, nActions: nActions}
}

func (r *RLTrainingRunner) CollectRollouts(stepsPerEnv int) OmniResult[[]EpisodeResult] {
	results := make([]EpisodeResult, r.nEnvs)
	var wg sync.WaitGroup
	sem := make(chan struct{}, r.workers)

	for env := 0; env < r.nEnvs; env++ {
		wg.Add(1)
		sem <- struct{}{}
		go func(envID int) {
			defer wg.Done()
			defer func() { <-sem }()
			totalReward := 0.0
			valueSum := 0.0
			state := make([]float64, r.dState)
			for i := range state {
				state[i] = math.Sin(float64(envID*100+i)) * 0.1
			}
			for step := 0; step < stepsPerEnv; step++ {
				action := (envID + step) % r.nActions
				reward := math.Sin(float64(step)*0.1+float64(envID)) * 0.5
				value := reward * 1.1
				totalReward += reward
				valueSum += value
				for i := range state {
					state[i] = math.Tanh(state[i] + float64(action)*0.01)
				}
			}
			discountReturn := 0.0
			g := 1.0
			for step := 0; step < stepsPerEnv; step++ {
				rew := math.Sin(float64(step)*0.1+float64(envID)) * 0.5
				discountReturn += g * rew
				g *= r.gamma
			}
			results[envID] = EpisodeResult{
				EnvID: envID, TotalReward: totalReward,
				Steps: stepsPerEnv, AvgValue: valueSum / float64(stepsPerEnv),
				DiscountReturn: discountReturn,
			}
		}(env)
	}
	wg.Wait()

	r.mu.Lock()
	r.episodes += r.nEnvs
	r.mu.Unlock()
	return OmniResult[[]EpisodeResult]{Data: results}
}

func (r *RLTrainingRunner) Stats() string {
	r.mu.Lock()
	defer r.mu.Unlock()
	return fmt.Sprintf("episodes=%d envs=%d gamma=%.2f", r.episodes, r.nEnvs, r.gamma)
}
