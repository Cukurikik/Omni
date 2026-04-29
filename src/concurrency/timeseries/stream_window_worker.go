package timeseries

import (
	"time"
	"context"
	"sync"
)

// OMNI CONCURRENCY LAYER: Stream Window Worker
// Manages tumbling windows over infinite streams.

type DataPoint struct {
	Timestamp time.Time
	Value     float64
}

type WindowResult struct {
	StartTime time.Time
	EndTime   time.Time
	Count     int
	Sum       float64
}

type WindowWorker struct {
	windowSize time.Duration
	stream     <-chan DataPoint
	results    chan WindowResult
	wg         sync.WaitGroup
}

func NewWindowWorker(windowSize time.Duration, stream <-chan DataPoint) *WindowWorker {
	return &WindowWorker{
		windowSize: windowSize,
		stream:     stream,
		results:    make(chan WindowResult, 100),
	}
}

func (w *WindowWorker) Start(ctx context.Context) <-chan WindowResult {
	w.wg.Add(1)
	go w.process(ctx)
	
	go func() {
		w.wg.Wait()
		close(w.results)
	}()
	
	return w.results
}

func (w *WindowWorker) process(ctx context.Context) {
	defer w.wg.Done()
	
	var currentWindowStart time.Time
	var sum float64
	var count int

	for {
		select {
		case <-ctx.Done():
			return
		case dp, ok := <-w.stream:
			if !ok {
				if count > 0 {
					w.emitWindow(currentWindowStart, sum, count)
				}
				return
			}

			if currentWindowStart.IsZero() {
				currentWindowStart = dp.Timestamp.Truncate(w.windowSize)
			}

			if dp.Timestamp.Sub(currentWindowStart) >= w.windowSize {
				w.emitWindow(currentWindowStart, sum, count)
				
				// Reset for next window
				currentWindowStart = dp.Timestamp.Truncate(w.windowSize)
				sum = 0
				count = 0
			}

			sum += dp.Value
			count++
		}
	}
}

func (w *WindowWorker) emitWindow(start time.Time, sum float64, count int) {
	w.results <- WindowResult{
		StartTime: start,
		EndTime:   start.Add(w.windowSize),
		Count:     count,
		Sum:       sum,
	}
}
