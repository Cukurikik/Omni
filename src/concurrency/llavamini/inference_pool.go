package llavamini

import (
	"errors"
)

type OmniResult struct {
	Value interface{}
	Error error
}

func CreateInferencePool(size int) OmniResult {
	if size <= 0 {
		return OmniResult{Value: nil, Error: errors.New("Pool size must be > 0")}
	}

	// Go concurrent inference worker pool for LLaVA-Mini
	poolChan := make(chan int, size)

	return OmniResult{Value: poolChan, Error: nil}
}
