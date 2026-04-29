package yesbutstream

import (
	"errors"
	"math"
	"sync"
)

// OMNI Result Monad Implementation
type Result[T any] struct {
	Value T
	Error error
}

func Ok[T any](val T) Result[T] {
	return Result[T]{Value: val, Error: nil}
}

func Err[T any](err string) Result[T] {
	return Result[T]{Error: errors.New(err)}
}

func (r Result[T]) IsOk() bool {
	return r.Error == nil
}

func (r Result[T]) Unwrap() T {
	if !r.IsOk() {
		panic(r.Error)
	}
	return r.Value
}

// OMNI Engine: YesBut Stream
// Goroutine broker for multi-modal constraint pairing and asynchronous pipeline validation.
type YesButEngine struct {
	bufferSize int
	mutex      sync.RWMutex
}

func NewYesButEngine(bufferSize int) *YesButEngine {
	return &YesButEngine{
		bufferSize: bufferSize,
	}
}

// Compute constraint resolution across asynchronous pipelines
func (e *YesButEngine) CalculatePipelineDivergence(incomingRates []float64) Result[float64] {
	e.mutex.RLock()
	defer e.mutex.RUnlock()

	if len(incomingRates) == 0 {
		return Err[float64]("Mathematical constraint: cannot compute divergence of zero-length pipeline stream")
	}

	var sum float64
	for _, rate := range incomingRates {
		if rate < 0 {
			return Err[float64]("Rate constraint violated: logically cannot process negative streams")
		}
		sum += rate
	}

	mean := sum / float64(len(incomingRates))

	var varianceSum float64
	for _, rate := range incomingRates {
		diff := rate - mean
		varianceSum += diff * diff
	}

	variance := varianceSum / float64(len(incomingRates))
	standardDeviation := math.Sqrt(variance)

	return Ok(standardDeviation)
}

func (e *YesButEngine) ValidateDataPairing(textTokens int, imgSize int) Result[bool] {
	if textTokens <= 0 || imgSize <= 0 {
		return Err[bool]("Zero-dimensional data pairing mathematically invalid")
	}

	ratio := float64(textTokens) / float64(imgSize)
	
	// Information theoretic bound for 'yesbut' contradiction
	if ratio > 50.0 || ratio < 0.02 {
		return Err[bool]("Modality imbalance creates divergent contradiction states")
	}

	return Ok(true)
}
