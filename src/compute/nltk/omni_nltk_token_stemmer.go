// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// NLTK Token Stemmer (OMNI Zero-Mock Implementation)
// Implements deterministic Porter stemming consonant-vowel (CVC) mathematical checks.

package compute

import (
	"errors"
	"strings"
)

type StemResult struct {
	Value bool
	Error error
}

func OkStemResult(val bool) StemResult {
	return StemResult{Value: val, Error: nil}
}

func ErrStemResult(err string) StemResult {
	return StemResult{Value: false, Error: errors.New(err)}
}

// Determines if a character mathematically functions as a consonant in context
func isConsonant(word string, i int) bool {
	char := word[i]
	if char == 'a' || char == 'e' || char == 'i' || char == 'o' || char == 'u' {
		return false
	}
	if char == 'y' {
		if i == 0 {
			return true
		}
		// If previous is vowel, y is consonant. If prev is consonant, y is vowel.
		return !isConsonant(word, i-1)
	}
	return true
}

// Emulates Porter Stemmer measure (m) calculation mathematically
func CalculatePorterMeasure(token string) StemResult {
	token = strings.ToLower(token)
	if len(token) == 0 {
		return ErrStemResult("Token cannot be empty.")
	}
	
	for i := 0; i < len(token); i++ {
		c := token[i]
		if c < 'a' || c > 'z' {
			return ErrStemResult("Token contains non-alphabetic characters.")
		}
	}

	m := 0
	state := 0 // 0 = searching for vowel, 1 = searching for consonant

	for i := 0; i < len(token); i++ {
		isCons := isConsonant(token, i)
		if state == 0 && !isCons {
			state = 1
		} else if state == 1 && isCons {
			state = 0
			m++
		}
	}

	// Returning boolean evaluation: Is m > 0 (common stemmer condition)
	return OkStemResult(m > 0)
}
