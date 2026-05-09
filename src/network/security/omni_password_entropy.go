package security

// omni_password_entropy.go — Algorithmic Password Strength Analyzer
// Layer: Network / Security
// Inspired by: Tzohar/PassLLM (Algorithmic baseline prior to LLM inference)
//
// Calculates Shannon Entropy and applies NIST SP 800-63B heuristic checks
// to prevent usage of weak, predictable password compositions. Zero mock.

import (
	"math"
	"strings"
	"unicode"
)

type PasswordStrength struct {
	EntropyBits float64
	Score       int // 0 to 4 (0: Weakest, 4: Strongest)
	Suggestions []string
	IsPwned     bool // Placeholder for future k-Anonymity HIBP integration
}

// EvaluateStrength calculates base Shannon entropy using character pool sizes.
func EvaluateStrength(password string) PasswordStrength {
	strength := PasswordStrength{
		EntropyBits: 0.0,
		Score:       0,
		Suggestions: []string{},
	}

	length := len(password)
	if length == 0 {
		strength.Suggestions = append(strength.Suggestions, "Password cannot be empty.")
		return strength
	}

	// Calculate Charset Pool Size
	var hasLower, hasUpper, hasDigit, hasSpecial bool
	for _, char := range password {
		if unicode.IsLower(char) {
			hasLower = true
		} else if unicode.IsUpper(char) {
			hasUpper = true
		} else if unicode.IsDigit(char) {
			hasDigit = true
		} else {
			hasSpecial = true
		}
	}

	poolSize := 0
	if hasLower {
		poolSize += 26
	}
	if hasUpper {
		poolSize += 26
	}
	if hasDigit {
		poolSize += 10
	}
	if hasSpecial {
		poolSize += 32 // Approximate number of special characters on US keyboard
	}

	if poolSize == 0 {
		poolSize = 1 // Prevent log2(0) if non-standard characters bypass checks
	}

	// Shannon Entropy: E = L * log2(R)
	strength.EntropyBits = float64(length) * math.Log2(float64(poolSize))

	// Common pattern penalties (e.g., "password123", "qwerty")
	lowerPass := strings.ToLower(password)
	if strings.Contains(lowerPass, "password") || strings.Contains(lowerPass, "qwerty") || strings.Contains(lowerPass, "123456") {
		strength.EntropyBits -= 20.0
		strength.Suggestions = append(strength.Suggestions, "Avoid common dictionary words and keyboard patterns.")
	}

	// Length checks (NIST recommends minimum 8)
	if length < 8 {
		strength.Suggestions = append(strength.Suggestions, "Password should be at least 8 characters long.")
	}

	// Scoring based on bits of entropy
	// < 28 bits = Very Weak (0)
	// 28 - 35 bits = Weak (1)
	// 36 - 59 bits = Reasonable (2)
	// 60 - 127 bits = Strong (3)
	// > 127 bits = Very Strong (4)
	if strength.EntropyBits < 28 {
		strength.Score = 0
	} else if strength.EntropyBits < 36 {
		strength.Score = 1
	} else if strength.EntropyBits < 60 {
		strength.Score = 2
	} else if strength.EntropyBits < 128 {
		strength.Score = 3
	} else {
		strength.Score = 4
	}

	return strength
}
