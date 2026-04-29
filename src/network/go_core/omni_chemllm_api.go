// Omni ChemLLMBench Evaluation API (Go)
package go_core
func NameToSmilesAccuracy(preds, golds []string) float64 {
	if len(golds) == 0 { return 0 }
	c := 0; for i, p := range preds { if i < len(golds) && p == golds[i] { c++ } }
	return float64(c) / float64(len(golds))
}
func PropertyMAE(preds, golds []float64) float64 {
	if len(golds) == 0 { return 0 }
	sum := 0.0; for i, p := range preds { if i < len(golds) { d := p - golds[i]; if d < 0 { d = -d }; sum += d } }
	return sum / float64(len(golds))
}
