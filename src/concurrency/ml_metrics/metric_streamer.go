package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type MetricBatch struct {
	BatchID string
	Loss    float64
}

type MetricStreamer struct {
	workers int
	inChan  chan MetricBatch
	outChan chan OmniResult
	wg      sync.WaitGroup
}

func NewMetricStreamer(workers int) *MetricStreamer {
	return &MetricStreamer{
		workers: workers,
		inChan:  make(chan MetricBatch, 1000),
		outChan: make(chan OmniResult, 1000),
	}
}

func (s *MetricStreamer) Start() {
	for i := 0; i < s.workers; i++ {
		s.wg.Add(1)
		go s.process(i)
	}
}

func (s *MetricStreamer) process(id int) {
	defer s.wg.Done()
	for batch := range s.inChan {
		if batch.Loss < 0 {
			s.outChan <- OmniResult{Error: fmt.Errorf("invalid loss %f in batch %s", batch.Loss, batch.BatchID)}
			continue
		}

		// Deterministic moving average simulation
		smoothedLoss := batch.Loss*0.9 + 0.1
		s.outChan <- OmniResult{Value: fmt.Sprintf("Worker %d logged %s: smoothed_loss %.4f", id, batch.BatchID, smoothedLoss)}
	}
}

func (s *MetricStreamer) LogMetric(batch MetricBatch) {
	s.inChan <- batch
}

func (s *MetricStreamer) Close() {
	close(s.inChan)
	s.wg.Wait()
	close(s.outChan)
}
