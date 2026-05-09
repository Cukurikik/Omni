// Omni INTERS Search Metrics (Go)
// Ref: DaoD/INTERS — MIT
package network_gocore

import "math"

func NDCG(ranked []string, relevant map[string]bool, k int) float64 {
	dcg := 0.0
	for i := 0; i < k && i < len(ranked); i++ {
		if relevant[ranked[i]] {
			dcg += 1.0 / math.Log2(float64(i+2))
		}
	}
	n := len(relevant)
	if n > k {
		n = k
	}
	idcg := 0.0
	for i := 0; i < n; i++ {
		idcg += 1.0 / math.Log2(float64(i+2))
	}
	if idcg == 0 {
		return 0
	}
	return math.Round(dcg/idcg*10000) / 10000
}

func MRR(ranked []string, relevant map[string]bool) float64 {
	for i, r := range ranked {
		if relevant[r] {
			return 1.0 / float64(i+1)
		}
	}
	return 0
}

func MAP(rankedLists [][]string, relevantSets []map[string]bool) float64 {
	total := 0.0
	for q, ranked := range rankedLists {
		ap := 0.0
		hits := 0
		for i, r := range ranked {
			if relevantSets[q][r] {
				hits++
				ap += float64(hits) / float64(i+1)
			}
		}
		if len(relevantSets[q]) > 0 {
			total += ap / float64(len(relevantSets[q]))
		}
	}
	if len(rankedLists) == 0 {
		return 0
	}
	return math.Round(total/float64(len(rankedLists))*10000) / 10000
}

