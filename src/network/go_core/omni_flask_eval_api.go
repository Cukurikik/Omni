// Omni FLASK Evaluation API (Go)
// Ref: kaistAI/FLASK — ICLR 2024
package network_gocore

import "math"

type SkillScores struct {
	LogicalThinking     float64 `json:"logical_thinking"`
	BackgroundKnowledge float64 `json:"background_knowledge"`
	ProblemHandling     float64 `json:"problem_handling"`
	Creativity          float64 `json:"creativity"`
	Comprehension       float64 `json:"comprehension"`
	Harmlessness        float64 `json:"harmlessness"`
}

func (s SkillScores) Overall() float64 {
	vals := []float64{s.LogicalThinking, s.BackgroundKnowledge, s.ProblemHandling,
		s.Creativity, s.Comprehension, s.Harmlessness}
	sum := 0.0
	for _, v := range vals {
		sum += v
	}
	return math.Round(sum/float64(len(vals))*10000) / 10000
}

type EvalResult struct {
	ModelName string      `json:"model_name"`
	Scores    SkillScores `json:"scores"`
	Overall   float64     `json:"overall"`
}

func EvaluateModel(name string, scores SkillScores) EvalResult {
	return EvalResult{ModelName: name, Scores: scores, Overall: scores.Overall()}
}

