// Omni UHGEval Hallucination API (Go)
package go_core
import "strings"
func HallucinationRatio(response, reference string) float64 {
	rt := toSet(strings.Fields(strings.ToLower(reference)))
	rsp := strings.Fields(strings.ToLower(response))
	if len(rsp) == 0 { return 0 }
	ungrounded := 0; for _, t := range rsp { if !rt[t] { ungrounded++ } }
	return float64(ungrounded) / float64(len(rsp))
}
func toSet(s []string) map[string]bool { m := map[string]bool{}; for _, v := range s { m[v] = true }; return m }
