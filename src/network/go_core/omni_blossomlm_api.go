// Omni BlossomLM Data Pipeline API (Go)
package network_gocore

import (
	"crypto/md5"
	"fmt"
)

func DeduplicateHash(texts []string) []string {
	seen := map[string]bool{}
	var result []string
	for _, t := range texts {
		h := fmt.Sprintf("%x", md5.Sum([]byte(t)))
		if !seen[h] {
			seen[h] = true
			result = append(result, t)
		}
	}
	return result
}
func QualityFilter(texts []string, minWords, maxWords int) []string {
	var result []string
	for _, t := range texts {
		n := len(t) / 5
		if n >= minWords && n <= maxWords {
			result = append(result, t)
		}
	}
	return result
}

