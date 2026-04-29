package netquant

import (
	"errors"
	"math"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type CalibrationBatch struct {
	BatchID string
	Tensors [][]float32
}

type CalibrationPool struct {
	workers int
	jobs    chan CalibrationBatch
	results chan OmniResult
	wg      sync.WaitGroup
}

func NewCalibrationPool(workers int, queueSize int) *CalibrationPool {
	return &CalibrationPool{
		workers: workers,
		jobs:    make(chan CalibrationBatch, queueSize),
		results: make(chan OmniResult, queueSize),
	}
}

func (p *CalibrationPool) Start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.calibrateWorker()
	}
}

func (p *CalibrationPool) calibrateWorker() {
	defer p.wg.Done()
	for batch := range p.jobs {
		if len(batch.Tensors) == 0 {
			p.results <- OmniResult{Error: errors.New("empty calibration batch")}
			continue
		}

		// Zero-mock mathematical aggregation of tensor statistics
		var maxAbs float32 = 0.0
		for _, tensor := range batch.Tensors {
			for _, val := range tensor {
				absVal := float32(math.Abs(float64(val)))
				if absVal > maxAbs {
					maxAbs = absVal
				}
			}
		}

		p.results <- OmniResult{Data: map[string]interface{}{
			"batch_id": batch.BatchID,
			"max_abs":  maxAbs,
			"scale":    maxAbs / 127.0,
		}}
	}
}

func (p *CalibrationPool) Submit(batch CalibrationBatch) OmniResult {
	select {
	case p.jobs <- batch:
		return OmniResult{Data: "queued"}
	default:
		return OmniResult{Error: errors.New("calibration pool saturated")}
	}
}

func (p *CalibrationPool) Stop() {
	close(p.jobs)
	p.wg.Wait()
	close(p.results)
}
