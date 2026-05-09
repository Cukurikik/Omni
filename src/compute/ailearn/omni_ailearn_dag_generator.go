// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// AILearn DAG Generator (OMNI Zero-Mock Implementation)
// Implements Kahn's Algorithm mathematically for topological DAG execution.

package compute

import "errors"

type DAGResult struct {
	Value []string
	Error error
}

func OkDAGResult(val []string) DAGResult {
	return DAGResult{Value: val, Error: nil}
}

func ErrDAGResult(err string) DAGResult {
	return DAGResult{Value: nil, Error: errors.New(err)}
}

type AILearnDAG struct {
	edges    map[string][]string
	inDegree map[string]int
}

func NewAILearnDAG() *AILearnDAG {
	return &AILearnDAG{
		edges:    make(map[string][]string),
		inDegree: make(map[string]int),
	}
}

func (d *AILearnDAG) AddNode(node string) {
	if _, exists := d.inDegree[node]; !exists {
		d.inDegree[node] = 0
		d.edges[node] = []string{}
	}
}

func (d *AILearnDAG) AddEdge(from, to string) {
	d.AddNode(from)
	d.AddNode(to)
	d.edges[from] = append(d.edges[from], to)
	d.inDegree[to]++
}

// Emits topological sorting of the directed acyclic graph
func (d *AILearnDAG) GenerateExecutionPlan() DAGResult {
	var queue []string
	var plan []string

	// Enqueue all nodes with 0 in-degree
	for node, degree := range d.inDegree {
		if degree == 0 {
			queue = append(queue, node)
		}
	}

	count := 0

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:] // Dequeue
		plan = append(plan, curr)
		count++

		for _, neighbor := range d.edges[curr] {
			d.inDegree[neighbor]--
			if d.inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	if count != len(d.inDegree) { // Cycle detected
		return ErrDAGResult("Acyclic execution failed: DAG contains a cycle.")
	}

	return OkDAGResult(plan)
}
