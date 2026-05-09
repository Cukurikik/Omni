package skillnet

import (
	"errors"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SkillGraph struct {
	Nodes map[string][]string
}

func (sg *SkillGraph) ResolveSkillPath(start string, target string) OmniResult {
	if sg.Nodes == nil || len(sg.Nodes) == 0 {
		return OmniResult{Value: nil, Error: errors.New("empty skill graph")}
	}

	// BFS for skill connection paths
	visited := make(map[string]bool)
	queue := [][]string{{start}}

	for len(queue) > 0 {
		path := queue[0]
		queue = queue[1:]

		node := path[len(path)-1]
		if node == target {
			return OmniResult{Value: path, Error: nil}
		}

		if !visited[node] {
			visited[node] = true
			for _, neighbor := range sg.Nodes[node] {
				newPath := append([]string{}, path...)
				newPath = append(newPath, neighbor)
				queue = append(queue, newPath)
			}
		}
	}

	return OmniResult{Value: nil, Error: errors.New("no path found")}
}
