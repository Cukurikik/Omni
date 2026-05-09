package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type TimeSeriesData struct {
	StreamID   string
	Datapoints []float64
}

type SeriesWorker struct {
	tasks   chan TimeSeriesData
	wg      sync.WaitGroup
	mu      sync.Mutex
	results map[string]float64
}

func NewSeriesWorker(bufferSize int) *SeriesWorker {
	return &SeriesWorker{
		tasks:   make(chan TimeSeriesData, bufferSize),
		results: make(map[string]float64),
	}
}

func (w *SeriesWorker) Start(numWorkers int) {
	for i := 0; i < numWorkers; i++ {
		w.wg.Add(1)
		go w.processLoop(i)
	}
}

func (w *SeriesWorker) SubmitStream(data TimeSeriesData) OmniResult {
	if data.StreamID == "" || len(data.Datapoints) == 0 {
		return OmniResult{Error: fmt.Errorf("invalid time series data")}
	}

	select {
	case w.tasks <- data:
		return OmniResult{Value: "Stream submitted for processing"}
	default:
		return OmniResult{Error: fmt.Errorf("stream queue full")}
	}
}

func (w *SeriesWorker) processLoop(workerID int) {
	defer w.wg.Done()

	for task := range w.tasks {
		// Deterministic rolling average processing
		var sum float64 = 0
		for _, v := range task.Datapoints {
			sum += v
		}
		avg := sum / float64(len(task.Datapoints))

		w.mu.Lock()
		w.results[task.StreamID] = avg
		w.mu.Unlock()
	}
}

func (w *SeriesWorker) Stop() {
	close(w.tasks)
	w.wg.Wait()
}
