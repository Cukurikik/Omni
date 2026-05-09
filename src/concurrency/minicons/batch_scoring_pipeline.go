// @omni-layer Concurrency | @omni-source kanishkamisra/minicons
// @omni-description Batch scoring pipeline in Go: concurrent LM scoring with
// work-stealing queue for high-throughput surprisal computation.
// @omni-lang Go | @omni-batch 16 | @omni-semester 16
package minicons

import (
	"math"
	"sync"
	"sync/atomic"
)

type ScoringTask struct {
	ID       int
	TokenIDs []int
}

type ScoringResult struct {
	ID         int
	Surprisals []float64
	MeanSurp   float64
	Perplexity float64
}

type BatchScoringPipeline struct {
	vocabSize int
	nWorkers  int
	processed int64
}

func NewBatchScoringPipeline(vocabSize, nWorkers int) *BatchScoringPipeline {
	return &BatchScoringPipeline{vocabSize: vocabSize, nWorkers: nWorkers}
}

func (p *BatchScoringPipeline) scoreSequence(tokenIDs []int) ScoringResult {
	n := len(tokenIDs)
	surprisals := make([]float64, n)
	totalLL := 0.0
	for i, tid := range tokenIDs {
		logProb := -math.Log(float64(p.vocabSize)) + math.Sin(float64(tid)*0.01)*0.5
		surprisals[i] = -logProb / math.Log(2)
		totalLL += logProb
	}
	avgLL := totalLL / math.Max(float64(n), 1)
	mean := 0.0
	for _, s := range surprisals {
		mean += s
	}
	mean /= math.Max(float64(n), 1)
	return ScoringResult{Surprisals: surprisals, MeanSurp: mean, Perplexity: math.Exp(-avgLL)}
}

func (p *BatchScoringPipeline) ProcessBatch(tasks []ScoringTask) []ScoringResult {
	results := make([]ScoringResult, len(tasks))
	taskCh := make(chan int, len(tasks))
	for i := range tasks {
		taskCh <- i
	}
	close(taskCh)
	var wg sync.WaitGroup
	for w := 0; w < p.nWorkers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for idx := range taskCh {
				r := p.scoreSequence(tasks[idx].TokenIDs)
				r.ID = tasks[idx].ID
				results[idx] = r
				atomic.AddInt64(&p.processed, 1)
			}
		}()
	}
	wg.Wait()
	return results
}

func (p *BatchScoringPipeline) GetProcessedCount() int64 {
	return atomic.LoadInt64(&p.processed)
}
