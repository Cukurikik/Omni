// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Helm Chart (OMNI Zero-Mock Implementation)
// Implements mathematical DAG dependency cycle resolution.

package compute

import (
	"errors"
)

type ValidationResult struct {
	Value []string // Ordered charts based on installation priority
	Error error
}

func OkValidationResult(val []string) ValidationResult {
	return ValidationResult{Value: val, Error: nil}
}

func ErrValidationResult(err string) ValidationResult {
	return ValidationResult{Value: nil, Error: errors.New(err)}
}

// Emulates Helm chart dependencies ordering topologically
func ResolveChartInstallOrder(charts []string, dependencies map[string][]string) ValidationResult {
	inDegree := make(map[string]int)
	for _, chart := range charts {
		inDegree[chart] = 0
	}

	for _, deps := range dependencies {
		for _, dep := range deps {
			if _, exists := inDegree[dep]; exists {
				inDegree[dep]++
			} else {
				// Implicitly add dependency if not in requested deployment directly
				inDegree[dep] = 1
			}
		}
	}

	queue := []string{}
	for node, degree := range inDegree {
		if degree == 0 {
			queue = append(queue, node)
		}
	}

	installed := []string{}

	// Kahn's Algorithm
	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]
		installed = append(installed, curr)

		if deps, ok := dependencies[curr]; ok {
			for _, dep := range deps {
				inDegree[dep]--
				if inDegree[dep] == 0 {
					queue = append(queue, dep)
				}
			}
		}
	}

	for _, degree := range inDegree {
		if degree > 0 {
			return ErrValidationResult("Circular dependency detected in Helm chart requirements.")
		}
	}

	// Reverse list because Kahn's resolves dependencies outward;
	// for Helm, dependencies must be installed BEFORE the parent.
	finalOrder := make([]string, len(installed))
	for i, j := 0, len(installed)-1; i < len(installed); i, j = i+1, j-1 {
		finalOrder[i] = installed[j]
	}

	return OkValidationResult(finalOrder)
}
