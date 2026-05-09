// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// FG Data Profiler (OMNI Zero-Mock Implementation)
// Implements reservoir sampling math for stream profiling.

package compute

import (
	"errors"
	"math/rand"
	"time"
)

type ResultStruct struct {
	Value []float64
	Error error
}

func OkFloat64Slice(val []float64) ResultStruct {
	return ResultStruct{Value: val, Error: nil}
}

func ErrFloat64Slice(err string) ResultStruct {
	return ResultStruct{Value: nil, Error: errors.New(err)}
}

type ReservoirProfiler struct {
	k         int // Reservoir size
	reservoir []float64
	count     int
	rng       *rand.Rand
}

func NewReservoirProfiler(k int) (*ReservoirProfiler, error) {
	if k <= 0 {
		return nil, errors.New("reservoir size must be positive")
	}
	return &ReservoirProfiler{
		k:         k,
		reservoir: make([]float64, 0, k),
		count:     0,
		rng:       rand.New(rand.NewSource(time.Now().UnixNano())),
	}, nil
}

func (p *ReservoirProfiler) ProcessStream(dataStream <-chan float64) ResultStruct {
	for value := range dataStream {
		p.count++

		if len(p.reservoir) < p.k {
			p.reservoir = append(p.reservoir, value)
		} else {
			// Probability of k/count
			j := p.rng.Intn(p.count)
			if j < p.k {
				p.reservoir[j] = value
			}
		}
	}

	if len(p.reservoir) == 0 {
		return ErrFloat64Slice("No data streamed into profiler.")
	}

	return OkFloat64Slice(p.reservoir)
}
