package oceangpt

import (
	"context"
	"errors"
)

type AcousticResult struct {
	RMSValue float64
	Signal   bool
}

type OceanRouter struct {
	NoiseFloor float64
}

// OMNI Network Layer - Ocean Acoustic Router
func (r *OceanRouter) EvaluateWave(ctx context.Context, rms float64) (*AcousticResult, error) {
	if rms < 0 {
		return nil, errors.New("negative RMS calculated")
	}
	
	return &AcousticResult{
		RMSValue: rms,
		Signal:   rms > r.NoiseFloor,
	}, nil
}
