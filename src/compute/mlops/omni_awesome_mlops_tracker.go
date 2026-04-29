// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Awesome MLOps Tracker (OMNI Zero-Mock Implementation)
// Implements strict monotonic commit tracking hash logic for experiments.

package compute

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"sort"
)

type HashResult struct {
	Value string
	Error error
}

func OkHashResult(val string) HashResult {
	return HashResult{Value: val, Error: nil}
}

func ErrHashResult(err string) HashResult {
	return HashResult{Value: "", Error: errors.New(err)}
}

type ExperimentMetadata struct {
	Hyperparameters map[string]float64
	DatasetHash     string
	Algorithm       string
}

// Generates an immutable, deterministic SHA256 tag for MLOps tracking.
func GenerateDeterministicExperimentId(metadata ExperimentMetadata) HashResult {
	if metadata.Algorithm == "" || metadata.DatasetHash == "" {
		return ErrHashResult("Algorithm and Dataset components must not be blank.")
	}
	
	// Order hyperparameters lexicographically to maintain determinism
	var hpKeys []string
	for k := range metadata.Hyperparameters {
		hpKeys = append(hpKeys, k)
	}
	sort.Strings(hpKeys)
	
	// Build deterministic string buffer
	var bufferString string
	bufferString += "ALG:" + metadata.Algorithm + "|"
	bufferString += "DATA:" + metadata.DatasetHash + "|"
	
	for _, k := range hpKeys {
		bufferString += fmt.Sprintf("%s:%f|", k, metadata.Hyperparameters[k])
	}
	
	hasher := sha256.New()
	hasher.Write([]byte(bufferString))
	hashed := hex.EncodeToString(hasher.Sum(nil))
	
	return OkHashResult(hashed)
}
