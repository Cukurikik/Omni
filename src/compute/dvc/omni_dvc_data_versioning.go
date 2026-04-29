// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// DVC Data Versioning Core (OMNI Zero-Mock Implementation)
// Implements Merkle Tree generation for dataset validation.

package dvc

import (
    "crypto/sha256"
    "encoding/hex"
    "errors"
)

type Result[T any] struct {
    Value T
    Error error
    IsOk  bool
}

func Ok[T any](val T) Result[T] {
    return Result[T]{Value: val, Error: nil, IsOk: true}
}

func Err[T any](err string) Result[T] {
    var zero T
    return Result[T]{Value: zero, Error: errors.New(err), IsOk: false}
}

type DatasetChunk struct {
    ID      string
    Content []byte
}

type DVCVersionEngine struct{}

func (e *DVCVersionEngine) HashDataChunk(content []byte) string {
    hash := sha256.Sum256(content)
    return hex.EncodeToString(hash[:])
}

// Compute the root Merkle hash deterministically given pre-ordered chunks
func (e *DVCVersionEngine) BuildMerkleRoot(chunks []DatasetChunk) Result[string] {
    if len(chunks) == 0 {
        return Err[string]("Dataset is empty, cannot version.")
    }
    
    hashes := make([]string, len(chunks))
    for i, chunk := range chunks {
        hashes[i] = e.HashDataChunk(chunk.Content)
    }
    
    for len(hashes) > 1 {
        var nextLevel []string
        for i := 0; i < len(hashes); i += 2 {
             if i+1 < len(hashes) {
                 combined := append([]byte(hashes[i]), []byte(hashes[i+1])...)
                 nextLevel = append(nextLevel, e.HashDataChunk(combined))
             } else {
                 nextLevel = append(nextLevel, hashes[i])
             }
        }
        hashes = nextLevel
    }
    
    return Ok(hashes[0])
}
