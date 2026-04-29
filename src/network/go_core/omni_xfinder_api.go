// Omni xFinder Evaluation API (Go)
package go_core
import "strings"
func ExtractMCAnswer(response string) string {
	lines := strings.Split(response, "\n")
	for i := len(lines) - 1; i >= 0; i-- {
		line := strings.TrimSpace(lines[i])
		for _, c := range "ABCD" {
			if strings.ContainsRune(strings.ToUpper(line), c) { return string(c) }
		}
	}
	return ""
}
func BatchAccuracy(preds, golds []string) float64 {
	if len(golds) == 0 { return 0 }
	c := 0; for i, p := range preds { if i < len(golds) && strings.EqualFold(p, golds[i]) { c++ } }
	return float64(c) / float64(len(golds))
}
