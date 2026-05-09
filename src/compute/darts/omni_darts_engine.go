// OMNI FRAMEWORK: BATCH 1 SEMESTER 14
// ENGINE: OMNI DARTS ENGINE
// DOMAIN: COMPUTE / TIME-SERIES FORECASTING (GO)
// ZERO MOCK - PRODUCTION READY
// ==========================================

package darts

import (
	"context"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
)

// DartsError defines custom error structures for time-series operations.
type DartsError struct {
	Code    string
	Message string
	Err     error
}

func (e *DartsError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("DartsError[%s]: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("DartsError[%s]: %s", e.Code, e.Message)
}

// Result is the standard OMNI monadic result.
type DartsResult[T any] struct {
	Value T
	Err   error
}

// TimeSeries represents an immutable sequence of data points.
type TimeSeries struct {
	Timestamps []int64
	Values     []float64
}

// OmniDartsEngine provides mathematical forecasting algorithms (Exponential Smoothing, MA).
type OmniDartsEngine struct {
	mu          sync.RWMutex
	seriesStore map[string]TimeSeries

	// Config
	alpha float64 // Smoothing factor for level
	beta  float64 // Smoothing factor for trend

	// Metrics
	forecastsDone atomic.Int64
	seriesStored  atomic.Int64
}

// NewOmniDartsEngine initializes the forecasting engine.
func NewOmniDartsEngine(alpha, beta float64) *OmniDartsEngine {
	return &OmniDartsEngine{
		seriesStore: make(map[string]TimeSeries),
		alpha:       alpha,
		beta:        beta,
	}
}

// Ingest stores a time series for later forecasting. O(1).
func (e *OmniDartsEngine) Ingest(id string, series TimeSeries) DartsResult[bool] {
	if len(series.Values) == 0 {
		return DartsResult[bool]{Err: &DartsError{Code: "EMPTY_SERIES", Message: "Cannot ingest empty time series"}}
	}
	if len(series.Timestamps) != len(series.Values) {
		return DartsResult[bool]{Err: &DartsError{Code: "MISMATCH", Message: "Timestamps length must match values length"}}
	}

	e.mu.Lock()
	defer e.mu.Unlock()

	e.seriesStore[id] = series
	e.seriesStored.Add(1)

	return DartsResult[bool]{Value: true}
}

// SimpleMovingAverage calculates SMA for the given series. O(N).
func (e *OmniDartsEngine) SimpleMovingAverage(id string, window int) DartsResult[[]float64] {
	e.mu.RLock()
	series, exists := e.seriesStore[id]
	e.mu.RUnlock()

	if !exists {
		return DartsResult[[]float64]{Err: &DartsError{Code: "NOT_FOUND", Message: "Series ID not found"}}
	}

	n := len(series.Values)
	if window <= 0 || window > n {
		return DartsResult[[]float64]{Err: &DartsError{Code: "INVALID_WINDOW", Message: "Window size must be between 1 and series length"}}
	}

	e.forecastsDone.Add(1)

	sma := make([]float64, n-window+1)
	var sum float64

	// Initial window sum
	for i := 0; i < window; i++ {
		sum += series.Values[i]
	}
	sma[0] = sum / float64(window)

	// Slide window
	for i := window; i < n; i++ {
		sum += series.Values[i] - series.Values[i-window]
		sma[i-window+1] = sum / float64(window)
	}

	return DartsResult[[]float64]{Value: sma}
}

// HoltLinearForecast implements Double Exponential Smoothing (Level + Trend) for forecasting.
// O(N) where N is length of series. Returns future steps.
func (e *OmniDartsEngine) HoltLinearForecast(ctx context.Context, id string, steps int) DartsResult[[]float64] {
	e.mu.RLock()
	series, exists := e.seriesStore[id]
	e.mu.RUnlock()

	if !exists {
		return DartsResult[[]float64]{Err: &DartsError{Code: "NOT_FOUND", Message: "Series ID not found"}}
	}

	n := len(series.Values)
	if n < 2 {
		return DartsResult[[]float64]{Err: &DartsError{Code: "INSUFFICIENT_DATA", Message: "Need at least 2 data points for Holt's linear"}}
	}

	e.forecastsDone.Add(1)

	level := series.Values[0]
	trend := series.Values[1] - series.Values[0]

	// Fit
	for i := 1; i < n; i++ {
		// Context check for large fits
		if i%1000 == 0 {
			select {
			case <-ctx.Done():
				return DartsResult[[]float64]{Err: ctx.Err()}
			default:
			}
		}

		lastLevel := level
		val := series.Values[i]

		level = e.alpha*val + (1-e.alpha)*(lastLevel+trend)
		trend = e.beta*(level-lastLevel) + (1-e.beta)*trend
	}

	// Forecast
	forecast := make([]float64, steps)
	for i := 0; i < steps; i++ {
		forecast[i] = level + float64(i+1)*trend
	}

	return DartsResult[[]float64]{Value: forecast}
}

// RMSE calculates Root Mean Square Error between true and predicted series.
func (e *OmniDartsEngine) RMSE(trueVals, predVals []float64) DartsResult[float64] {
	if len(trueVals) != len(predVals) {
		return DartsResult[float64]{Err: &DartsError{Code: "MISMATCH", Message: "Series lengths must match for RMSE"}}
	}
	if len(trueVals) == 0 {
		return DartsResult[float64]{Err: &DartsError{Code: "EMPTY", Message: "Cannot compute RMSE of empty arrays"}}
	}

	var sqErrSum float64
	for i := 0; i < len(trueVals); i++ {
		err := trueVals[i] - predVals[i]
		sqErrSum += err * err
	}

	return DartsResult[float64]{Value: math.Sqrt(sqErrSum / float64(len(trueVals)))}
}

// Diagnostics returns system state metrics.
func (e *OmniDartsEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":         "OmniDartsEngine",
		"version":        "1.0.0-production",
		"series_stored":  e.seriesStored.Load(),
		"forecasts_done": e.forecastsDone.Load(),
		"alpha":          e.alpha,
		"beta":           e.beta,
		"status":         "operational",
	}
}
