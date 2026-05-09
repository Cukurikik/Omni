// Omni PanelGPT Prompting API (Go)
package network_gocore

import "fmt"

func BuildPanelPrompt(question string, roles []string) string {
	if len(roles) < 3 {
		roles = append(roles, "Expert", "Expert", "Expert")
	}
	return fmt.Sprintf("Experts %s, %s, %s discuss: %s\nConsensus:", roles[0], roles[1], roles[2], question)
}
func ConsistencyScore(answers []string) float64 {
	if len(answers) < 2 {
		return 1.0
	}
	same := 0
	total := 0
	for i := 0; i < len(answers); i++ {
		for j := i + 1; j < len(answers); j++ {
			total++
			if answers[i] == answers[j] {
				same++
			}
		}
	}
	if total == 0 {
		return 0
	}
	return float64(same) / float64(total)
}

