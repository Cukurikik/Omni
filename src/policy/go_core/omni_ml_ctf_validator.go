package security

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
)

// Omni ML CTF Validator (Go)
// Based on Machine_Learning_CTF_Challenges
// Validates cryptographic signatures of adversarial input payloads.

type ValidationResult struct {
	IsValid bool
	Flag    string
}

func ValidateAdversarialPayload(payload []byte, expectedHash string) (ValidationResult, error) {
	if len(payload) == 0 {
		return ValidationResult{}, errors.New("payload cannot be empty")
	}
	if expectedHash == "" {
		return ValidationResult{}, errors.New("expected hash cannot be empty")
	}

	hash := sha256.Sum256(payload)
	computedHash := hex.EncodeToString(hash[:])

	if computedHash == expectedHash {
		// Deterministic CTF flag generation for valid adversarial bypass
		flag := "OMNI_CTF{" + computedHash[:8] + "}"
		return ValidationResult{IsValid: true, Flag: flag}, nil
	}

	return ValidationResult{IsValid: false, Flag: ""}, nil
}
