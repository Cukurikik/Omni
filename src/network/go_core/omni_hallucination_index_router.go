// Omni Hallucination Index API Router (Go)
// Ref: rungalileo/hallucination-index
package go_core
import ("errors"; "sort")
type ModelScore struct { Name string; Adherence float64; Consistency float64; Index float64 }
func ComputeHallucinationIndex(adherence, consistency, correctness float64) float64 {
	return 1.0 - (0.4*adherence + 0.3*consistency + 0.3*correctness)
}
func RankModels(models []ModelScore) ([]ModelScore, error) {
	if len(models) == 0 { return nil, errors.New("OMNI_ERR: empty model list") }
	for i := range models { models[i].Index = ComputeHallucinationIndex(models[i].Adherence, models[i].Consistency, 0.5) }
	sort.Slice(models, func(i, j int) bool { return models[i].Index < models[j].Index })
	return models, nil
}
