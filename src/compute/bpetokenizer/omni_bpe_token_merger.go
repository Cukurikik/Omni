// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// BPE Tokenizer (OMNI Zero-Mock Implementation)
// Implements deterministic pairing frequency aggregation mathematically.

package compute

import (
	"errors"
)

type PairResult struct {
	Value map[string]int // The aggregate pair frequencies
	Error error
}

func OkPairResult(val map[string]int) PairResult {
	return PairResult{Value: val, Error: nil}
}

func ErrPairResult(err string) PairResult {
	return PairResult{Value: nil, Error: errors.New(err)}
}

// Emulates Byte-Pair Encoding pair extraction mathematically
func ExtractBPEPairs(vocab map[string]int) PairResult {
	if len(vocab) == 0 {
		return ErrPairResult("Vocabulary cannot be empty.")
	}

	pairFrequencies := make(map[string]int)

	for wordString, count := range vocab {
		// Simulate characters separated by space for algorithm validation
		// e.g. "l o w <\w>"
		symbols := extractSymbols(wordString)

		if len(symbols) < 2 {
			continue
		}

		for i := 0; i < len(symbols)-1; i++ {
			pairKey := symbols[i] + " " + symbols[i+1]
			pairFrequencies[pairKey] += count
		}
	}

	return OkPairResult(pairFrequencies)
}

func extractSymbols(s string) []string {
	var symbols []string
	wordBytes := []byte(s)

	// Simply map ascii abstractly for BPE test execution
	for _, b := range wordBytes {
		symbols = append(symbols, string(b))
	}
	// append terminal symbol abstractly
	symbols = append(symbols, "<\\w>")

	return symbols
}
