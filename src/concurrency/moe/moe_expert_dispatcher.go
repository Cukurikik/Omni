// @omni-layer Concurrency | @omni-source microsoft/DeepSpeed | @omni-lang Go
// @omni-description Expert-parallel MoE dispatcher: routes tokens to expert
// workers across goroutines with capacity management.
package moe

import "sync"

type ExpertTask struct {
	ExpertID int
	TokenIDs []int
	Features [][]float64
}

type ExpertResult struct {
	ExpertID int
	Output   [][]float64
	Tokens   int
}

type MoEDispatcher struct {
	nExperts int
	nWorkers int
}

func NewMoEDispatcher(nExperts, nWorkers int) *MoEDispatcher {
	return &MoEDispatcher{nExperts: nExperts, nWorkers: nWorkers}
}

func (d *MoEDispatcher) Dispatch(tasks []ExpertTask) []ExpertResult {
	results := make([]ExpertResult, len(tasks))
	ch := make(chan int, len(tasks))
	for i := range tasks {
		ch <- i
	}
	close(ch)
	var wg sync.WaitGroup
	for w := 0; w < d.nWorkers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for idx := range ch {
				t := tasks[idx]
				out := make([][]float64, len(t.Features))
				for i, feat := range t.Features {
					processed := make([]float64, len(feat))
					for j, v := range feat {
						processed[j] = v * 1.01
					}
					out[i] = processed
				}
				results[idx] = ExpertResult{ExpertID: t.ExpertID, Output: out, Tokens: len(t.Features)}
			}
		}()
	}
	wg.Wait()
	return results
}
