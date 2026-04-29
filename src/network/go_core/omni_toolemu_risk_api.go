// Omni ToolEmu Risk API (Go)
// Ref: ryoungj/ToolEmu — Apache-2.0
package go_core
import "strings"
type RiskResult struct { Tool string; Score float64; Level string; Flags []string }
var dangerousActions = map[string]float64{"delete":0.9,"write":0.6,"execute":0.8,"send":0.5,"transfer":0.7}
func AssessRisk(tool, action string, args []string) RiskResult {
	score := 0.0; var flags []string
	for da, w := range dangerousActions {
		if strings.Contains(strings.ToLower(action), da) {
			if w > score { score = w }; flags = append(flags, "action_"+da)
		}
	}
	level := "low"; if score > 0.7 { level = "critical" } else if score > 0.4 { level = "high" }
	return RiskResult{Tool: tool, Score: score, Level: level, Flags: flags}
}
