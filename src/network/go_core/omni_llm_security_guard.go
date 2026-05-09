// Omni LLM Security Guard (Go)
// Ref: forcesunseen/llm-hackers-handbook
package network_gocore

import "strings"

var injectionPatterns = []string{"ignore previous", "disregard instructions", "system prompt", "jailbreak", "do anything now"}

func DetectInjection(text string) (bool, []string) {
	t := strings.ToLower(text)
	var found []string
	for _, p := range injectionPatterns {
		if strings.Contains(t, p) {
			found = append(found, p)
		}
	}
	return len(found) > 0, found
}
func SanitizeInput(text string) string {
	for _, p := range injectionPatterns {
		text = strings.ReplaceAll(strings.ToLower(text), p, "[FILTERED]")
	}
	return text
}

