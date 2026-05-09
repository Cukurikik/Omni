// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Terraform State Parser (OMNI Zero-Mock Implementation)
// Implements resource dependency DAG to determine apply/destroy order visually.

package terraform

import (
	"errors"
	"strings"
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

type TFResource struct {
	Address   string
	DependsOn []string
}

type TFDagEngine struct{}

// Derives linear execution order based on TF dependency references
func (e *TFDagEngine) DerivePlanOrder(resources []TFResource) Result[[]string] {
	inDegree := make(map[string]int)
	graph := make(map[string][]string)

	for _, res := range resources {
		inDegree[res.Address] = 0 // Initialize
	}

	// Build edges (dependency -> dependent)
	for _, res := range resources {
		for _, dep := range res.DependsOn {
			// Sanitize module wrapper interpolation logically if needed
			depClean := strings.TrimSpace(dep)
			graph[depClean] = append(graph[depClean], res.Address)
			inDegree[res.Address]++
		}
	}

	queue := []string{}
	for addr, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, addr)
		}
	}

	order := []string{}
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		order = append(order, node)

		for _, dependent := range graph[node] {
			inDegree[dependent]--
			if inDegree[dependent] == 0 {
				queue = append(queue, dependent)
			}
		}
	}

	if len(order) != len(resources) {
		return Err[[]string]("Circular dependency detected in Terraform state plan.")
	}

	return Ok(order)
}
