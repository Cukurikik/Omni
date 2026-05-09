// Omni SubgraphRAG Query API (Go)
package network_gocore

type Triple struct{ Head, Rel, Tail string }

func ExtractSubgraph(adj map[string][]Triple, seeds []string, maxHops int) []Triple {
	visited := map[string]bool{}
	for _, s := range seeds {
		visited[s] = true
	}
	frontier := seeds
	var result []Triple
	for h := 0; h < maxHops; h++ {
		var next []string
		for _, node := range frontier {
			for _, t := range adj[node] {
				result = append(result, t)
				if !visited[t.Tail] {
					visited[t.Tail] = true
					next = append(next, t.Tail)
				}
			}
		}
		frontier = next
	}
	return result
}

