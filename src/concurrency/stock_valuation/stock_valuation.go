package stockvaluation

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

// OMNI Engine: Multi-Modal Valuation Forecast
// Goroutine math broker for bounded economic trajectory estimation vectors.
type ValuationEngine struct {
	baseInterestRate float64
	mutex            sync.RWMutex
}

func NewValuationEngine(interestRate float64) *ValuationEngine {
	return &ValuationEngine{
		baseInterestRate: interestRate,
	}
}

// Calculate Discounted Cash Flow limits using an asynchronous matrix map
func (e *ValuationEngine) CalculateDCFMatrix(cashFlows []float64, riskPremium float64) Result[float64] {
	e.mutex.RLock()
	defer e.mutex.RUnlock()

	if len(cashFlows) == 0 {
		return Err[float64]("Degenerate matrix: Empty cash flows yield trivial zero")
	}

	discountRate := e.baseInterestRate + riskPremium
	if discountRate <= 0.0 {
		return Err[float64]("Economic singularity: discount rate cannot be <= 0")
	}

	var dcf float64
	for t, flow := range cashFlows {
		// Enforce time dimensionality
		year := float64(t + 1)
		discountFactor := math.Pow(1.0+discountRate, year)

		if math.IsInf(discountFactor, 1) {
			return Err[float64]("Mathematical overflow: discount factor diverges")
		}

		dcf += flow / discountFactor
	}

	return Ok(dcf)
}

func (e *ValuationEngine) ComputeVolatilitySpread(highs []float64, lows []float64) Result[float64] {
	if len(highs) != len(lows) {
		return Err[float64]("Dimension mismatch between high and low vectors")
	}
	if len(highs) == 0 {
		return Err[float64]("Input array degenerate")
	}

	var spreadSum float64
	for i := 0; i < len(highs); i++ {
		diff := highs[i] - lows[i]
		if diff < 0 {
			return Err[float64]("Market logic violation: low > high")
		}
		spreadSum += diff
	}

	return Ok(spreadSum / float64(len(highs)))
}
