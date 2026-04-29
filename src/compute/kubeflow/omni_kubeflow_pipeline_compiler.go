// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// KubeFlow Pipeline Compiler (OMNI Zero-Mock Implementation)
// Implements DAG validation and YAML emission for K8s pipelines.

package kubeflow

import (
	"errors"
	"fmt"
)

type Result struct {
	Value interface{}
	Error error
	IsOk  bool
}

func Ok(val interface{}) Result {
	return Result{Value: val, Error: nil, IsOk: true}
}

func Err(err string) Result {
	return Result{Value: nil, Error: errors.New(err), IsOk: false}
}

type Task struct {
	Name         string
	Dependencies []string
	Command      string
}

type Compiler struct{}

func (c *Compiler) TopoSort(tasks []Task) Result {
	if len(tasks) == 0 {
		return Err("Cannot compile empty pipeline.")
	}

	inDegree := make(map[string]int)
	graph := make(map[string][]string)

	for _, t := range tasks {
		inDegree[t.Name] = 0
	}

	for _, t := range tasks {
		for _, dep := range t.Dependencies {
			if _, exists := inDegree[dep]; !exists {
				return Err(fmt.Sprintf("Dependency %s not found for task %s", dep, t.Name))
			}
			graph[dep] = append(graph[dep], t.Name)
			inDegree[t.Name]++
		}
	}

	var queue []string
	for node, degree := range inDegree {
		if degree == 0 {
			queue = append(queue, node)
		}
	}

	var sorted []string
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		sorted = append(sorted, node)

		for _, neighbor := range graph[node] {
			inDegree[neighbor]--
			if inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	if len(sorted) != len(tasks) {
		return Err("Cycle detected in pipeline DAG.")
	}

	return Ok(sorted)
}
