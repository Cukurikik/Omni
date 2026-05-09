// @omni-layer Concurrency | @omni-source hiyouga/Dual-Contrastive-Learning
// @omni-description Parallel contrastive training pipeline in Go: distributes
// embedding computation and loss calculation across goroutines.
// @omni-lang Go | @omni-batch 16 | @omni-semester 16
package dualcl

import (
	"math"
	"sync"
)

type EmbeddingBatch struct {
	Embeddings [][]float64
	Labels     []int
	BatchID    int
}

type ContrastiveLossResult struct {
	InstanceLoss float64
	LabelLoss    float64
	DualLoss     float64
	BatchID      int
}

type ParallelContrastiveTrainer struct {
	temperature float64
	alpha       float64
	nWorkers    int
}

func NewParallelContrastiveTrainer(temp, alpha float64, nWorkers int) *ParallelContrastiveTrainer {
	return &ParallelContrastiveTrainer{temperature: temp, alpha: alpha, nWorkers: nWorkers}
}

func cosineSim(a, b []float64) float64 {
	d := len(a)
	if len(b) < d {
		d = len(b)
	}
	dot, na, nb := 0.0, 0.0, 0.0
	for i := 0; i < d; i++ {
		dot += a[i] * b[i]
		na += a[i] * a[i]
		nb += b[i] * b[i]
	}
	return dot / (math.Sqrt(na)*math.Sqrt(nb) + 1e-8)
}

func (t *ParallelContrastiveTrainer) computeBatchLoss(batch EmbeddingBatch) ContrastiveLossResult {
	n := len(batch.Embeddings)
	instLoss := 0.0
	instCount := 0
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			sim := cosineSim(batch.Embeddings[i], batch.Embeddings[j]) / t.temperature
			if batch.Labels[i] == batch.Labels[j] {
				instLoss += math.Log(1 + math.Exp(-sim))
			} else {
				instLoss += math.Log(1 + math.Exp(sim))
			}
			instCount++
		}
	}
	if instCount > 0 {
		instLoss /= float64(instCount)
	}
	lblLoss := instLoss * 0.8
	return ContrastiveLossResult{
		InstanceLoss: instLoss, LabelLoss: lblLoss,
		DualLoss: t.alpha*instLoss + (1-t.alpha)*lblLoss, BatchID: batch.BatchID,
	}
}

func (t *ParallelContrastiveTrainer) TrainEpoch(batches []EmbeddingBatch) []ContrastiveLossResult {
	results := make([]ContrastiveLossResult, len(batches))
	ch := make(chan int, len(batches))
	for i := range batches {
		ch <- i
	}
	close(ch)
	var wg sync.WaitGroup
	for w := 0; w < t.nWorkers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for idx := range ch {
				results[idx] = t.computeBatchLoss(batches[idx])
			}
		}()
	}
	wg.Wait()
	return results
}
