package sanitization

import (
	"errors"
	"strings"
)

// OMNI MOTHER SYSTEM - SECURITY LAYER
// GraphQL Query Depth Limiter.
// Strictly prevents DOS attacks on API endpoints by calculating the structural depth of incoming GraphQL queries.

var (
	ErrQueryTooDeep = errors.New("OMNI_FATAL: GraphQL query exceeds maximum allowed depth")
	ErrMalformed    = errors.New("OMNI_FATAL: Malformed GraphQL query brackets")
)

type QueryValidator struct {
	MaxDepth int
}

func NewQueryValidator(maxDepth int) *QueryValidator {
	return &QueryValidator{MaxDepth: maxDepth}
}

// CalculateDepth parses the raw string without a full AST overhead to quickly reject malicious payloads.
// Note: In production, this can also hook into `graphql-go` AST walker for semantic precision.
// This implements a structural bracket-matching tokenizer for extreme zero-allocation speed.
func (v *QueryValidator) CalculateDepth(rawQuery string) (int, error) {
	if rawQuery == "" {
		return 0, nil
	}

	maxDepth := 0
	currentDepth := 0
	inString := false

	// Fast single-pass rune check
	for i := 0; i < len(rawQuery); i++ {
		char := rawQuery[i]

		// Handle string literals (ignore brackets inside strings)
		if char == '"' {
			// Check for escape character \"
			if i > 0 && rawQuery[i-1] != '\\' {
				inString = !inString
			}
			continue
		}

		if inString {
			continue
		}

		switch char {
		case '{':
			currentDepth++
			if currentDepth > maxDepth {
				maxDepth = currentDepth
			}
			if maxDepth > v.MaxDepth {
				return maxDepth, ErrQueryTooDeep
			}
		case '}':
			currentDepth--
			if currentDepth < 0 {
				return 0, ErrMalformed
			}
		}
	}

	if currentDepth != 0 {
		return 0, ErrMalformed // Unbalanced brackets
	}

	// Subtract 1 because the root operation (query { ... }) is usually considered depth 0
	if maxDepth > 0 {
		maxDepth--
	}

	return maxDepth, nil
}

// EnsureSafe executes the depth check and returns an error if unsafe.
func (v *QueryValidator) EnsureSafe(rawQuery string) error {
	_, err := v.CalculateDepth(rawQuery)
	return err
}

// StripComments removes GraphQL comments (#...) which might obfuscate query length analysis.
func (v *QueryValidator) StripComments(rawQuery string) string {
	lines := strings.Split(rawQuery, "\n")
	var result strings.Builder

	for _, line := range lines {
		if idx := strings.Index(line, "#"); idx != -1 {
			result.WriteString(line[:idx])
		} else {
			result.WriteString(line)
		}
		result.WriteString("\n")
	}

	return result.String()
}
