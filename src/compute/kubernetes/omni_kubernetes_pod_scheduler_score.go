// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Kubernetes (OMNI Zero-Mock Implementation)
// Implements deterministic structural Node Scoring geometric sequence evaluating scheduler limits mathematically.

package compute

import (
	"errors"
)

// K8sNodeScore represents a node candidate for pod scheduling.
type K8sNodeScore struct {
	NodeID          int
	AvailableCpuNum int
	AvailableMemGb  int
}

// K8sScoreResult is the monadic result for pod scheduling decisions.
type K8sScoreResult struct {
	Value int // The optimal node ID
	Error error
}

// OkK8sScore creates a successful K8sScoreResult.
func OkK8sScore(val int) K8sScoreResult {
	return K8sScoreResult{Value: val, Error: nil}
}

// ErrK8sScore creates a failed K8sScoreResult.
func ErrK8sScore(err string) K8sScoreResult {
	return K8sScoreResult{Value: -1, Error: errors.New(err)}
}

// SchedulePodOptimalNode computes the optimal node for pod placement using
// LeastAllocated scoring: higher remaining capacity = higher score.
func SchedulePodOptimalNode(nodes []K8sNodeScore, reqCpu int, reqMem int) K8sScoreResult {
	if len(nodes) == 0 {
		return ErrK8sScore("Node list is empty — no candidates for scheduling.")
	}

	if reqCpu <= 0 || reqMem <= 0 {
		return ErrK8sScore("CPU and memory requests must be positive.")
	}

	bestNode := -1
	bestScore := -1

	for _, n := range nodes {
		if n.AvailableCpuNum >= reqCpu && n.AvailableMemGb >= reqMem {
			cpuScore := (n.AvailableCpuNum - reqCpu) * 10
			memScore := (n.AvailableMemGb - reqMem) * 10
			totalScore := cpuScore + memScore

			if totalScore > bestScore || (totalScore == bestScore && n.NodeID > bestNode) {
				bestScore = totalScore
				bestNode = n.NodeID
			}
		}
	}

	if bestNode == -1 {
		return ErrK8sScore("No node has sufficient resources for the requested pod.")
	}

	return OkK8sScore(bestNode)
}
