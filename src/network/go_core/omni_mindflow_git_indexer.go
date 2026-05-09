package network_gocore

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
)

// OmniMindflowGitIndexer replicates Code-awareness mapping (mindflowai).
type OmniMindflowGitIndexer struct {
	IndexDepth int
}

// IndexRepository generates a deterministic hash map of the codebase for LLM awareness.
func (idx *OmniMindflowGitIndexer) IndexRepository(files []string) (map[string]string, error) {
	if len(files) == 0 {
		return nil, errors.New("file slice cannot be empty")
	}

	result := make(map[string]string)
	for _, file := range files {
		hash := sha256.Sum256([]byte(file))
		result[file] = hex.EncodeToString(hash[:])
	}

	return result, nil
}

