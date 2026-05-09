package gpt4all

import (
	"context"
	"errors"
)

type QuatResult struct {
	Magnitude  float64
	Normalized bool
}

type UnityRouter struct {
	Epsilon float64
}

// OMNI Network Layer - GPT4All Unity Quaternion Router
func (r *UnityRouter) ProcessQuaternion(ctx context.Context, mag float64) (*QuatResult, error) {
	if mag < 0 {
		return nil, errors.New("magnitude cannot be negative")
	}

	diff := mag - 1.0
	if diff < 0 {
		diff = -diff
	}

	return &QuatResult{
		Magnitude:  mag,
		Normalized: diff <= r.Epsilon,
	}, nil
}
