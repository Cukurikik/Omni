// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Caire Seam Carving (OMNI Zero-Mock Implementation)
// Implements deterministic dynamic programming seam energy calculation.

package compute

import (
	"errors"
	"math"
)

type SeamResult struct {
	Value []int // The x coordinate path of the lowest energy seam
	Error error
}

func OkSeamResult(val []int) SeamResult {
	return SeamResult{Value: val, Error: nil}
}

func ErrSeamResult(err string) SeamResult {
	return SeamResult{Value: nil, Error: errors.New(err)}
}

// EnergyMatrix is an abstracted HxW float64 map of pixel energies
func CalculateOptimalVerticalSeam(energyMatrix [][]float64) SeamResult {
	height := len(energyMatrix)
	if height == 0 {
		return ErrSeamResult("Matrix cannot be empty.")
	}
	width := len(energyMatrix[0])
	if width == 0 {
		return ErrSeamResult("Matrix width cannot be empty.")
	}

	// DP table
	dp := make([][]float64, height)
	for i := range dp {
		dp[i] = make([]float64, width)
	}

	// First row
	for x := 0; x < width; x++ {
		dp[0][x] = energyMatrix[0][x]
	}

	// Dynamic Programming pass
	for y := 1; y < height; y++ {
		for x := 0; x < width; x++ {
			bestPrev := dp[y-1][x]
			if x > 0 && dp[y-1][x-1] < bestPrev {
				bestPrev = dp[y-1][x-1]
			}
			if x < width-1 && dp[y-1][x+1] < bestPrev {
				bestPrev = dp[y-1][x+1]
			}
			dp[y][x] = energyMatrix[y][x] + bestPrev
		}
	}

	// Backtrack to find the path
	path := make([]int, height)
	minVal := math.MaxFloat64
	minIdx := -1

	for x := 0; x < width; x++ {
		if dp[height-1][x] < minVal {
			minVal = dp[height-1][x]
			minIdx = x
		}
	}
	path[height-1] = minIdx

	for y := height - 2; y >= 0; y-- {
		prevX := path[y+1]
		bestX := prevX
		bestVal := dp[y][prevX]

		if prevX > 0 && dp[y][prevX-1] < bestVal {
			bestX = prevX - 1
			bestVal = dp[y][bestX]
		}
		if prevX < width-1 && dp[y][prevX+1] < bestVal {
			bestX = prevX + 1
		}
		
		path[y] = bestX
	}

	return OkSeamResult(path)
}
