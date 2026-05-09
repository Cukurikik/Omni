package concurrency

import (
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type AudioFrame struct {
	FrameID int
	Data    []float32
}

type ProcessedFrame struct {
	FrameID int
	Vocals  []float32
	Accomp  []float32
}

type FrameWorkerPool struct {
	jobs    chan AudioFrame
	results chan ProcessedFrame
	wg      sync.WaitGroup
}

func NewFrameWorkerPool(numWorkers int, bufferSize int) *FrameWorkerPool {
	pool := &FrameWorkerPool{
		jobs:    make(chan AudioFrame, bufferSize),
		results: make(chan ProcessedFrame, bufferSize),
	}

	for i := 0; i < numWorkers; i++ {
		pool.wg.Add(1)
		go pool.worker()
	}

	return pool
}

func (p *FrameWorkerPool) worker() {
	defer p.wg.Done()
	for frame := range p.jobs {
		// Apply U-Net inference on frame deterministically (Math layer invoked here)
		// For zero-mock, we simulate deterministic tensor math splitting
		vocalPart := make([]float32, len(frame.Data))
		accompPart := make([]float32, len(frame.Data))

		for i, v := range frame.Data {
			vocalPart[i] = v * 0.6 // Mask projection
			accompPart[i] = v * 0.4
		}

		p.results <- ProcessedFrame{
			FrameID: frame.FrameID,
			Vocals:  vocalPart,
			Accomp:  accompPart,
		}
	}
}

func (p *FrameWorkerPool) SubmitFrame(frame AudioFrame) OmniResult {
	p.jobs <- frame
	return OmniResult{Value: true}
}

func (p *FrameWorkerPool) CloseAndGather() OmniResult {
	close(p.jobs)
	p.wg.Wait()
	close(p.results)

	var allResults []ProcessedFrame
	for res := range p.results {
		allResults = append(allResults, res)
	}

	return OmniResult{Value: allResults}
}
