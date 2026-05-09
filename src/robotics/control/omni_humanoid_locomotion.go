package locomotion

import (
	"context"
	"math"
	"sync"
	"time"
)

// HLT: Humanoid Locomotion with Transformers
// Implements the reinforcement learning policy event loop mapping proprioceptive state to joint torques.

type JointState struct {
	Position float32
	Velocity float32
	Torque   float32
}

type ProprioceptiveObservation struct {
	Joints      [12]JointState // 12 DOF for humanoid lower body
	Orientation [4]float32         // Quaternion
	LinearVel   [3]float32
	AngularVel  [3]float32
}

type HLTTransformerPolicy struct {
	mu           sync.Mutex
	HistoryLen   int
	StateHistory []ProprioceptiveObservation
}

func NewHLTPolicy(historyLen int) *HLTTransformerPolicy {
	return &HLTTransformerPolicy{
		HistoryLen:   historyLen,
		StateHistory: make([]ProprioceptiveObservation, 0, historyLen),
	}
}

// PredictTorques simulates the transformer forward pass using historical context
func (p *HLTTransformerPolicy) PredictTorques(ctx context.Context, currentObs ProprioceptiveObservation) ([12]float32, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	// Update history ring buffer
	if len(p.StateHistory) >= p.HistoryLen {
		p.StateHistory = p.StateHistory[1:]
	}
	p.StateHistory = append(p.StateHistory, currentObs)

	var targetTorques [12]float32
	if len(p.StateHistory) < 5 {
		// Not enough context, return zero torques
		return targetTorques, nil
	}

	// Simulate self-attention over history for joint 0-11
	for j := 0; j < 12; j++ {
		var temporalSum float32
		for i, obs := range p.StateHistory {
			weight := float32(i) / float32(len(p.StateHistory)) // simplified attention weight
			temporalSum += obs.Joints[j].Position * weight
		}
		// PD control simulated output
		targetTorques[j] = float32(math.Tanh(float64(temporalSum))) * 30.0 // Max 30 Nm torque
	}

	return targetTorques, nil
}

func ControlLoop(ctx context.Context, policy *HLTTransformerPolicy, sensorCh <-chan ProprioceptiveObservation, actuatorCh chan<- [12]float32) {
	ticker := time.NewTicker(20 * time.Millisecond) // 50Hz control loop
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case obs := <-sensorCh:
			torques, err := policy.PredictTorques(ctx, obs)
			if err == nil {
				select {
				case actuatorCh <- torques:
				default:
					// Drop frame if actuator cannot keep up
				}
			}
		}
	}
}

