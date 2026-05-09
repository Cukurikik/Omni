// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Kubernetes Scheduler (OMNI Zero-Mock Implementation)
// Implements deterministic Node Scoring math for Pod placement.

package compute

import (
	"errors"
)

type ScoreResult struct {
	Value map[string]int
	Error error
}

func OkScoreResult(val map[string]int) ScoreResult {
	return ScoreResult{Value: val, Error: nil}
}

func ErrScoreResult(err string) ScoreResult {
	return ScoreResult{Value: nil, Error: errors.New(err)}
}

type NodeMetrics struct {
	ID                string
	CPUAvailableMil   int
	MemoryAvailableMB int
	PodCount          int
}

type PodRequirements struct {
	CPURequestMil   int
	MemoryRequestMB int
}

// ComputeNodeScores implements simplified mathematical Priority Score function (LeastRequestedPriority)
func ComputeNodeScores(nodes []NodeMetrics, podReq PodRequirements) ScoreResult {
	if len(nodes) == 0 {
		return ErrScoreResult("Node list cannot be empty for scheduling.")
	}

	scores := make(map[string]int)

	for _, node := range nodes {
		// Filter Phase (Predicates)
		if node.CPUAvailableMil < podReq.CPURequestMil || node.MemoryAvailableMB < podReq.MemoryRequestMB {
			scores[node.ID] = 0 // Infeasible node
			continue
		}

		// Score Phase (Priorities)
		// 10 is max score. Formula: (cpu((capacity-sum(requested))*10/capacity) + memory((capacity-sum(requested))*10/capacity)) / 2
		cpuScore := (node.CPUAvailableMil - podReq.CPURequestMil) * 10 / node.CPUAvailableMil
		memScore := (node.MemoryAvailableMB - podReq.MemoryRequestMB) * 10 / node.MemoryAvailableMB

		// Balanced resource allocation average
		finalScore := (cpuScore + memScore) / 2

		// Small heuristic penalization for current pod counts to encourage spread
		finalScore -= node.PodCount / 10
		if finalScore < 1 {
			finalScore = 1 // Min feasible score
		}

		scores[node.ID] = finalScore
	}

	return OkScoreResult(scores)
}
