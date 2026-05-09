package concurrency

// Result is the monadic result type for this engine.
type Result struct {
	Value interface{}
	Error error
}

type GPUQueueError struct {
	Msg string
}

func (e *GPUQueueError) Error() string {
	return "GPU Queue Fault: " + e.Msg
}

// OMNI Engine: gpu-queue-pool
// Mathematical queue density limits for physical node mapping.
type GPUTaskQueueEngine struct {
	MaxConcurrentVRAMBytes int64
}

func NewGPUTaskQueueEngine(maxBytes int64) *GPUTaskQueueEngine {
	return &GPUTaskQueueEngine{MaxConcurrentVRAMBytes: maxBytes}
}

func (e *GPUTaskQueueEngine) CalculateQueueFragmentation(activeTasks int, totalAllocatedBytes int64) Result {
	if activeTasks <= 0 && totalAllocatedBytes > 0 {
		return Result{nil, &GPUQueueError{Msg: "Ghost memory mapping (Bytes allocated without active tasks)"}}
	}

	if totalAllocatedBytes > e.MaxConcurrentVRAMBytes {
		return Result{nil, &GPUQueueError{Msg: "VRAM geometry structurally breached"}}
	}

	if activeTasks == 0 {
		return Result{map[string]interface{}{"fragmentation_ratio": 0.0}, nil}
	}

	averageBytesPerTask := float64(totalAllocatedBytes) / float64(activeTasks)
	capacityRatio := float64(totalAllocatedBytes) / float64(e.MaxConcurrentVRAMBytes)

	// An approximation, many small tasks = higher fragmentation risk
	fragmentationRisk := (1.0 - (averageBytesPerTask / float64(e.MaxConcurrentVRAMBytes))) * capacityRatio

	return Result{map[string]interface{}{
		"fragmentation_risk_score": fragmentationRisk,
		"is_critical":              fragmentationRisk > 0.8,
	}, nil}
}

func (e *GPUTaskQueueEngine) ComputeMutexWaitProbability(queueLength int, dispatchRateHz float64) Result {
	if dispatchRateHz <= 0.0 {
		return Result{nil, &GPUQueueError{Msg: "Dispatch dimension collapsed to zero"}}
	}

	waitExpectedSec := float64(queueLength) / dispatchRateHz

	return Result{map[string]interface{}{
		"expected_wait_sec": waitExpectedSec,
		"probability_lock":  waitExpectedSec > 1.0,
	}, nil}
}
