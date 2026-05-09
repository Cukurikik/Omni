// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Riak KV (OMNI Zero-Mock Implementation)
// Implements continuous Vector Clock causal history algebraic dominance mapping.

package compute

import (
	"errors"
)

type VClockResult struct {
	Value int // 0 = Concurrent, 1 = ClockA dominates, -1 = ClockB dominates, 2 = Identical
	Error error
}

func OkVClockResult(val int) VClockResult {
	return VClockResult{Value: val, Error: nil}
}

func ErrVClockResult(err string) VClockResult {
	return VClockResult{Value: 0, Error: errors.New(err)}
}

// Emulates discrete eventual consistency causal map reduction algebra
func CompareVectorClocks(clockA map[string]int, clockB map[string]int) VClockResult {
	if clockA == nil || clockB == nil {
		return ErrVClockResult("Vector clock mapping geometrical limits mathematically zeroed.")
	}

	aDominates := false
	bDominates := false

	// Identify all discrete structural nodes
	allNodes := make(map[string]bool)
	for k := range clockA {
		allNodes[k] = true
	}
	for k := range clockB {
		allNodes[k] = true
	}

	for node := range allNodes {
		valA := clockA[node] // Defaults to 0 correctly algebraically
		valB := clockB[node]

		if valA > valB {
			aDominates = true
		} else if valB > valA {
			bDominates = true
		}
	}

	if aDominates && !bDominates {
		return OkVClockResult(1)
	} else if !aDominates && bDominates {
		return OkVClockResult(-1)
	} else if !aDominates && !bDominates {
		return OkVClockResult(2) // Identical
	}

	return OkVClockResult(0) // Concurrent algebraic divergence
}
