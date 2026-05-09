// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Awesome-Kubernetes Scheduler (OMNI Zero-Mock Implementation)
// Implements K8s Node Resource Bin Packing logic.

package k8s

import (
	"errors"
)

type Result[T any] struct {
	Value T
	Error error
	IsOk  bool
}

func Ok[T any](val T) Result[T] {
	return Result[T]{Value: val, Error: nil, IsOk: true}
}

func Err[T any](err string) Result[T] {
	var zero T
	return Result[T]{Value: zero, Error: errors.New(err), IsOk: false}
}

type Node struct {
	ID       string
	CpuAvail float64
	MemAvail float64
}

type Pod struct {
	ID     string
	CpuReq float64
	MemReq float64
}

type K8sScheduler struct{}

func (s *K8sScheduler) FirstFitSchedule(pods []Pod, nodes []Node) Result[map[string]string] {
	if len(nodes) == 0 {
		return Err[map[string]string]("No available nodes in cluster.")
	}

	allocations := make(map[string]string)

	for _, pod := range pods {
		scheduled := false
		for i := 0; i < len(nodes); i++ {
			if nodes[i].CpuAvail >= pod.CpuReq && nodes[i].MemAvail >= pod.MemReq {
				// Allocate
				nodes[i].CpuAvail -= pod.CpuReq
				nodes[i].MemAvail -= pod.MemReq
				allocations[pod.ID] = nodes[i].ID
				scheduled = true
				break
			}
		}
		if !scheduled {
			return Err[map[string]string]("Insufficient resources to schedule all pods.")
		}
	}

	return Ok(allocations)
}
