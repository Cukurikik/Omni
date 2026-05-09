// Omni SynLogic Verification API (Go)
// Ref: MiniMax-AI/SynLogic — MIT
package network_gocore

func CheckSAT(clauses [][]int, assignment map[int]bool) bool {
	for _, clause := range clauses {
		sat := false
		for _, lit := range clause {
			v := lit
			if v < 0 {
				v = -v
			}
			val, ok := assignment[v]
			if !ok {
				continue
			}
			if (lit > 0 && val) || (lit < 0 && !val) {
				sat = true
				break
			}
		}
		if !sat {
			return false
		}
	}
	return true
}
func ReasoningAccuracy(preds, golds []bool) float64 {
	if len(golds) == 0 {
		return 0
	}
	c := 0
	for i, p := range preds {
		if i < len(golds) && p == golds[i] {
			c++
		}
	}
	return float64(c) / float64(len(golds))
}

