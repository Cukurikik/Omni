// Omni AutoAgents Question Router (Go)
// Ref: AutoLLM/AutoAgents — MIT
package go_core

import "strings"

type AgentStep struct {
	Step     int    `json:"step"`
	Question string `json:"question"`
	Tool     string `json:"tool"`
	Status   string `json:"status"`
}

func DecomposeQuestion(question string) []string {
	connectors := []string{" and ", " or ", " also ", " then "}
	parts := []string{question}
	for _, conn := range connectors {
		var newParts []string
		for _, p := range parts {
			newParts = append(newParts, strings.Split(p, conn)...)
		}
		parts = newParts
	}
	var cleaned []string
	for _, p := range parts {
		t := strings.TrimSpace(p)
		if t != "" { cleaned = append(cleaned, t) }
	}
	return cleaned
}

func PlanSteps(subQuestions []string) []AgentStep {
	steps := make([]AgentStep, len(subQuestions))
	for i, sq := range subQuestions {
		tool := "reason"
		if strings.Contains(sq, "?") { tool = "search" }
		steps[i] = AgentStep{Step: i + 1, Question: sq, Tool: tool, Status: "pending"}
	}
	return steps
}
