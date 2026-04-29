// Omni REFLECT Action Logger (Go)
// Ref: real-stanford/reflect — CoRL 2023
package go_core
type ActionLog struct { Type string; Success bool; Error string; Step int }
type Summary struct { Total int; Successes int; Rate float64; CommonFail string }
func Summarize(logs []ActionLog) Summary {
	s := Summary{Total: len(logs)}
	failMap := map[string]int{}
	for _, l := range logs {
		if l.Success { s.Successes++ } else { failMap[l.Error]++ }
	}
	s.Rate = float64(s.Successes) / float64(max(s.Total, 1))
	for k, v := range failMap {
		if s.CommonFail == "" || v > failMap[s.CommonFail] { s.CommonFail = k }
	}
	return s
}
func max(a, b int) int { if a > b { return a }; return b }
