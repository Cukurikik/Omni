// Omni Magikarp Token Analyzer (Go)
// Ref: cohere-ai/magikarp — Apache-2.0
package go_core
import "math"
func DetectGlitchTokens(logprobs map[string]float64, thresholdStd float64) []string {
	vals := make([]float64, 0, len(logprobs))
	for _, v := range logprobs { vals = append(vals, v) }
	if len(vals) == 0 { return nil }
	sum := 0.0; for _, v := range vals { sum += v }; mean := sum / float64(len(vals))
	varSum := 0.0; for _, v := range vals { varSum += (v - mean) * (v - mean) }
	std := math.Sqrt(varSum / float64(len(vals)))
	thresh := mean - thresholdStd*std
	var glitch []string
	for tok, lp := range logprobs { if lp < thresh { glitch = append(glitch, tok) } }
	return glitch
}
