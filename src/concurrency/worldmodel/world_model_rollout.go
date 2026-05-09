// @omni-layer Concurrency | @omni-source lucidrains/genie2-pytorch | @omni-lang Go
// @omni-description World model rollout engine: concurrent multi-trajectory
// generation with action sampling and frame prediction pipeline.
package worldmodel

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type FrameTokens struct {
	FrameID int
	Tokens  []int
	Action  int
}

type Trajectory struct {
	ID     int
	Frames []FrameTokens
	Reward float64
}

type WorldModelRollout struct {
	mu           sync.Mutex
	codebookSz   int
	nTokens      int
	nActions     int
	workers      int
	trajectories []Trajectory
}

func NewWorldModelRollout(codebookSz, nTokens, nActions, workers int) *WorldModelRollout {
	return &WorldModelRollout{
		codebookSz: codebookSz, nTokens: nTokens,
		nActions: nActions, workers: workers,
	}
}

func (w *WorldModelRollout) predictNextFrame(tokens []int, action int) []int {
	next := make([]int, len(tokens))
	for i, t := range tokens {
		offset := (action*7 + t) % w.codebookSz
		noise := (t * (action + 1)) % 5
		next[i] = (t + offset + noise) % w.codebookSz
	}
	return next
}

func (w *WorldModelRollout) computeReward(trajectory []FrameTokens) float64 {
	if len(trajectory) < 2 {
		return 0
	}
	diversity := 0.0
	for i := 1; i < len(trajectory); i++ {
		diff := 0
		for j := 0; j < len(trajectory[i].Tokens) && j < len(trajectory[i-1].Tokens); j++ {
			if trajectory[i].Tokens[j] != trajectory[i-1].Tokens[j] {
				diff++
			}
		}
		diversity += float64(diff) / float64(len(trajectory[i].Tokens))
	}
	return math.Tanh(diversity / float64(len(trajectory)-1))
}

func (w *WorldModelRollout) GenerateTrajectories(initTokens []int, nTrajectories, horizon int) OmniResult[[]Trajectory] {
	results := make([]Trajectory, nTrajectories)
	var wg sync.WaitGroup
	sem := make(chan struct{}, w.workers)

	for t := 0; t < nTrajectories; t++ {
		wg.Add(1)
		sem <- struct{}{}
		go func(tid int) {
			defer wg.Done()
			defer func() { <-sem }()
			frames := make([]FrameTokens, 0, horizon+1)
			current := make([]int, len(initTokens))
			copy(current, initTokens)
			frames = append(frames, FrameTokens{FrameID: 0, Tokens: current, Action: -1})
			for h := 0; h < horizon; h++ {
				action := (tid*7 + h*3) % w.nActions
				next := w.predictNextFrame(current, action)
				frames = append(frames, FrameTokens{FrameID: h + 1, Tokens: next, Action: action})
				current = next
			}
			reward := w.computeReward(frames)
			results[tid] = Trajectory{ID: tid, Frames: frames, Reward: reward}
		}(t)
	}
	wg.Wait()

	w.mu.Lock()
	w.trajectories = append(w.trajectories, results...)
	w.mu.Unlock()
	return OmniResult[[]Trajectory]{Data: results}
}

func (w *WorldModelRollout) Stats() string {
	w.mu.Lock()
	defer w.mu.Unlock()
	return fmt.Sprintf("trajectories=%d", len(w.trajectories))
}
