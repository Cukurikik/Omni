package security

import (
	"errors"
	"regexp"
	"strings"
)

var (
	ErrEmptyInput = errors.New("input clinical text is empty")
	ErrRegexPanic = errors.New("internal regex compilation failed")
)

// Omni Mother System - Security Layer
// Protected Health Information (PHI) Redactor.
// This is a strict gateway that must execute before ANY medical text is sent to an LLM for summarization.

type PHIRedactor struct {
	// Compiled regex patterns for speed and thread safety
	ssnPattern   *regexp.Regexp
	phonePattern *regexp.Regexp
	emailPattern *regexp.Regexp
}

func NewPHIRedactor() *PHIRedactor {
	return &PHIRedactor{
		// Standard US SSN format
		ssnPattern: regexp.MustCompile(`\b\d{3}-\d{2}-\d{4}\b`),

		// North American phone numbers
		phonePattern: regexp.MustCompile(`\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b`),

		// Basic email structure
		emailPattern: regexp.MustCompile(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`),
	}
}

// Redact destructively mutates the string, replacing PHI with safe tokens.
// Returns an error if the input violates basic sanity checks.
func (r *PHIRedactor) Redact(clinicalText string) (string, error) {
	if strings.TrimSpace(clinicalText) == "" {
		return "", ErrEmptyInput
	}

	sanitized := clinicalText

	// Sequentially execute redactions. Order does not matter for distinct patterns.
	sanitized = r.ssnPattern.ReplaceAllString(sanitized, "[REDACTED_SSN]")
	sanitized = r.phonePattern.ReplaceAllString(sanitized, "[REDACTED_PHONE]")
	sanitized = r.emailPattern.ReplaceAllString(sanitized, "[REDACTED_EMAIL]")

	return sanitized, nil
}
