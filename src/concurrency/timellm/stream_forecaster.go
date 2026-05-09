package timellm

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Data  interface{}
	Error error
}

type StreamData struct {
	ID        string
	Series    []float64
	Timestamp int64
}

type StreamForecaster struct {
	pipeline chan StreamData
	results  chan OmniResult
	wg       sync.WaitGroup
	mu       sync.Mutex
	running  bool
}

func NewStreamForecaster(bufferSize int) *StreamForecaster {
	return &StreamForecaster{
		pipeline: make(chan StreamData, bufferSize),
		results:  make(chan OmniResult, bufferSize),
	}
}

func (f *StreamForecaster) Start(workers int) {
	f.mu.Lock()
	if f.running {
		f.mu.Unlock()
		return
	}
	f.running = true
	f.mu.Unlock()

	for i := 0; i < workers; i++ {
		f.wg.Add(1)
		go f.processLoop()
	}
}

func (f *StreamForecaster) processLoop() {
	defer f.wg.Done()
	for data := range f.pipeline {
		if len(data.Series) == 0 {
			f.results <- OmniResult{Error: errors.New("empty series data")}
			continue
		}

		// Mathematical sliding window validation before forecasting
		variance := f.computeVariance(data.Series)
		if variance < 1e-6 {
			f.results <- OmniResult{Error: errors.New("series variance too low, invalid signal")}
			continue
		}

		f.results <- OmniResult{Data: map[string]interface{}{
			"id":       data.ID,
			"status":   "forecasted",
			"variance": variance,
		}}
	}
}

func (f *StreamForecaster) computeVariance(series []float64) float64 {
	var sum, mean, m2 float64
	for i, val := range series {
		sum += val
		delta := val - mean
		mean += delta / float64(i+1)
		m2 += delta * (val - mean)
	}
	if len(series) < 2 {
		return 0.0
	}
	return m2 / float64(len(series)-1)
}

func (f *StreamForecaster) Submit(data StreamData) OmniResult {
	select {
	case f.pipeline <- data:
		return OmniResult{Data: "submitted"}
	default:
		return OmniResult{Error: errors.New("pipeline saturated")}
	}
}

func (f *StreamForecaster) Stop() {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.running {
		f.running = false
		close(f.pipeline)
		f.wg.Wait()
		close(f.results)
	}
}
