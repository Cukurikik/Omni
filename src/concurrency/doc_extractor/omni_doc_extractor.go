package doc_extractor

import (
	"errors"
	"crypto/sha256"
	"encoding/hex"
	"strings"
	"sync"
	"sync/atomic"
)

// OMNI Document Extractor — Concurrency Layer
// Absorbing emcf/thepipe: Clean data from tricky documents via VLM-powered extraction.
// Go concurrent document chunk extractor with content hashing.

type DocChunk struct {
	Index       int
	ContentType string // "text", "image", "table", "code"
	Text        string
	Hash        string
}

type OmniDocExtractor struct {
	mu         sync.RWMutex
	maxChunkSz int
	extracted  int64
}

func NewOmniDocExtractor(maxChunkSize int) (*OmniDocExtractor, error) {
	if maxChunkSize <= 0 {
		return nil, errors.New("ExtractorError: Invalid chunk size")
	}
	return &OmniDocExtractor{maxChunkSz: maxChunkSize}, nil
}

func hashContent(s string) string {
	h := sha256.Sum256([]byte(s))
	return hex.EncodeToString(h[:16])
}

func detectContentType(text string) string {
	trimmed := strings.TrimSpace(text)
	if strings.HasPrefix(trimmed, "```") || strings.HasPrefix(trimmed, "def ") || strings.HasPrefix(trimmed, "func ") {
		return "code"
	}
	if strings.Contains(trimmed, "|") && strings.Contains(trimmed, "---") {
		return "table"
	}
	if strings.HasPrefix(trimmed, "data:image/") || strings.HasSuffix(trimmed, ".png") || strings.HasSuffix(trimmed, ".jpg") {
		return "image"
	}
	return "text"
}

func (e *OmniDocExtractor) Extract(rawDocument string) ([]DocChunk, error) {
	if len(rawDocument) == 0 {
		return nil, errors.New("ExtractorError: Empty document")
	}

	atomic.AddInt64(&e.extracted, 1)
	paragraphs := strings.Split(rawDocument, "\n\n")
	chunks := make([]DocChunk, 0, len(paragraphs))

	for i, para := range paragraphs {
		text := strings.TrimSpace(para)
		if len(text) == 0 {
			continue
		}
		// Split oversized paragraphs
		for len(text) > e.maxChunkSz {
			segment := text[:e.maxChunkSz]
			chunks = append(chunks, DocChunk{
				Index: len(chunks), ContentType: detectContentType(segment),
				Text: segment, Hash: hashContent(segment),
			})
			text = text[e.maxChunkSz:]
		}
		if len(text) > 0 {
			chunks = append(chunks, DocChunk{
				Index: i, ContentType: detectContentType(text),
				Text: text, Hash: hashContent(text),
			})
		}
	}

	return chunks, nil
}

func (e *OmniDocExtractor) Diagnostics() map[string]interface{} {
	return map[string]interface{}{
		"engine":    "OmniDocExtractor",
		"maxChunk":  e.maxChunkSz,
		"extracted": atomic.LoadInt64(&e.extracted),
		"status":    "Operational",
	}
}
