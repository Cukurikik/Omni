package pysc2

import (
	"errors"
	"context"
)

type EnvBridge struct {
	Active bool
}

func NewEnvBridge() *EnvBridge {
	return &EnvBridge{Active: true}
}

func (b *EnvBridge) Step(ctx context.Context, action []float32) ([]float32, float32, bool, error) {
	if !b.Active {
		return nil, 0, false, errors.New("environment is inactive")
	}
	// Simulated PySC2 step
	obs := []float32{1.0, 0.5, 0.2}
	reward := float32(10.0)
	done := false
	return obs, reward, done, nil
}
