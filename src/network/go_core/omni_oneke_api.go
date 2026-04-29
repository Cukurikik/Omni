// Omni OneKE Knowledge Extract API (Go)
package go_core
import "strings"
func ExtractEntities(text string, schema []string) []map[string]string {
	words := strings.Fields(text); var results []map[string]string
	for _, w := range words {
		if len(w) > 2 && w[0] >= 'A' && w[0] <= 'Z' {
			etype := "Entity"; if len(schema) > 0 { etype = schema[0] }
			results = append(results, map[string]string{"text": w, "type": etype})
		}
	}
	return results
}
