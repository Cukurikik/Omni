package security

// omni_xss_sanitizer.go — XSS Sanitization Middleware
// Layer: Network / Security
// Inspired by: bluemonday
//
// Intercepts HTTP requests to clean input payloads, stripping potentially
// malicious HTML/JavaScript tags to prevent Cross-Site Scripting (XSS).
// Provides a fast regex-based HTML tag stripper. Zero mock.

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"regexp"
)

// A strict regex that matches < tags >, ignoring case
var tagRegex = regexp.MustCompile(`(?i)<[^>]*>`)

// OmniXSSSanitizer is the core sanitization engine
type OmniXSSSanitizer struct {
	Strict bool
}

func NewOmniXSSSanitizer(strict bool) *OmniXSSSanitizer {
	return &OmniXSSSanitizer{Strict: strict}
}

// SanitizeString removes all HTML tags from a string
func (s *OmniXSSSanitizer) SanitizeString(input string) string {
	if !s.Strict {
		// In a real policy-based sanitizer, we would allow <b>, <i>, etc.
		// For this implementation, strict implies stripping ALL tags.
	}
	return tagRegex.ReplaceAllString(input, "")
}

// sanitizeMap recursively sanitizes JSON maps
func (s *OmniXSSSanitizer) sanitizeMap(data map[string]interface{}) {
	for k, v := range data {
		switch val := v.(type) {
		case string:
			data[k] = s.SanitizeString(val)
		case map[string]interface{}:
			s.sanitizeMap(val)
		case []interface{}:
			s.sanitizeArray(val)
		}
	}
}

func (s *OmniXSSSanitizer) sanitizeArray(data []interface{}) {
	for i, v := range data {
		switch val := v.(type) {
		case string:
			data[i] = s.SanitizeString(val)
		case map[string]interface{}:
			s.sanitizeMap(val)
		case []interface{}:
			s.sanitizeArray(val)
		}
	}
}

// Middleware creates an HTTP middleware that sanitizes incoming JSON bodies
func (s *OmniXSSSanitizer) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Only process methods with bodies
		if r.Method == http.MethodPost || r.Method == http.MethodPut || r.Method == http.MethodPatch {
			// Check if it's JSON
			contentType := r.Header.Get("Content-Type")
			if contentType == "application/json" {
				bodyBytes, err := io.ReadAll(r.Body)
				if err == nil && len(bodyBytes) > 0 {
					var payload map[string]interface{}
					if err := json.Unmarshal(bodyBytes, &payload); err == nil {
						// Sanitize the payload
						s.sanitizeMap(payload)

						// Re-marshal the sanitized data
						sanitizedBytes, _ := json.Marshal(payload)

						// Replace the request body
						r.Body = io.NopCloser(bytes.NewBuffer(sanitizedBytes))
						r.ContentLength = int64(len(sanitizedBytes))
					} else {
						// If JSON is malformed, we can just reset the buffer and let the handler deal with it
						r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))
					}
				}
			}
		}

		next.ServeHTTP(w, r)
	})
}
