package go_pkg

import (
	"fmt"
	"regexp"
	"strings"
)

// OMNI Framework - Prompt Injection Sanitizer (Go)
// Inspects incoming requests at the Gateway level to detect and neutralize
// prompt injection attacks before they reach the MoE Ensemble.

type OmniSanitizer struct {
	blockedPatterns []*regexp.Regexp
}

func NewOmniSanitizer() *OmniSanitizer {
	fmt.Println("OMNI Go: Initializing Prompt Sanitizer.")
	return &OmniSanitizer{
		blockedPatterns: []*regexp.Regexp{
			regexp.MustCompile(`(?i)ignore previous instructions`),
			regexp.MustCompile(`(?i)system prompt`),
			regexp.MustCompile(`(?i)you are now a`),
		},
	}
}

func (s *OmniSanitizer) IsSafe(prompt string) bool {
	for _, pattern := range s.blockedPatterns {
		if pattern.MatchString(prompt) {
			fmt.Printf("OMNI Security Alert: Detected prompt injection pattern: %s\n", pattern.String())
			return false
		}
	}
	return true
}

func (s *OmniSanitizer) Sanitize(prompt string) string {
	// Simple neutralization - replace restricted strings
	safePrompt := prompt
	for _, pattern := range s.blockedPatterns {
		safePrompt = pattern.ReplaceAllString(safePrompt, "[REDACTED]")
	}
	return strings.TrimSpace(safePrompt)
}

