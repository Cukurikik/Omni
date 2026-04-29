// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Weaviate (OMNI Zero-Mock Implementation)
// Implements BM25 Inverted Index Term Frequency inverse math logic.

package weaviate

import (
	"errors"
	"math"
)

type BM25Result struct {
	Value float64
	Error error
}

func OkBM25Result(val float64) BM25Result {
	return BM25Result{Value: val, Error: nil}
}

func ErrBM25Result(err string) BM25Result {
	return BM25Result{Value: 0.0, Error: errors.New(err)}
}

// Emulates BM25 term weighting component mathematically
func ComputeBM25Score(termFreqInDoc int, docLength int, avgDocLength float64, totalDocs int, docsContainingTerm int, k1 float64, b float64) BM25Result {
	if avgDocLength <= 0 {
		return ErrBM25Result("Average document length must be strictly positive.")
	}
	if totalDocs <= 0 || docsContainingTerm < 0 || docsContainingTerm > totalDocs {
		return ErrBM25Result("Invalid document count boundaries.")
	}

	tf := float64(termFreqInDoc)
	dl := float64(docLength)
	
	// Inverse Document Frequency (IDF) with smoothing
	idfNum := float64(totalDocs - docsContainingTerm) + 0.5
	idfDen := float64(docsContainingTerm) + 0.5
	idf := math.Log(1.0 + (idfNum / idfDen))

	// Term Frequency Normalization bounds
	num := tf * (k1 + 1.0)
	den := tf + k1*(1.0-b+b*(dl/avgDocLength))

	score := idf * (num / den)
	return OkBM25Result(score)
}
