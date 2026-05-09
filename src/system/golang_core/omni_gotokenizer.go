// OMNI System — Go Tokenizers Port
// Go implementation of today's most used tokenizers (BPE, WordPiece).
package tokenizer

import (
	"strings"
	"sync"
)

// PreTrainedTokenizer defines the interface for all tokenizers.
type PreTrainedTokenizer interface {
	Tokenize(text string) []string
	ConvertTokensToIds(tokens []string) []int
	ConvertIdsToTokens(ids []int) []string
}

// BertWordPieceTokenizer implements the WordPiece subword algorithm.
type BertWordPieceTokenizer struct {
	vocab                map[string]int
	invVocab             map[int]string
	unkToken             string
	maxInputCharsPerWord int
	mu                   sync.RWMutex
}

func NewBertWordPieceTokenizer(vocab map[string]int) *BertWordPieceTokenizer {
	inv := make(map[int]string)
	for k, v := range vocab {
		inv[v] = k
	}
	return &BertWordPieceTokenizer{
		vocab:                vocab,
		invVocab:             inv,
		unkToken:             "[UNK]",
		maxInputCharsPerWord: 200,
	}
}

func (t *BertWordPieceTokenizer) whitespaceTokenize(text string) []string {
	text = strings.TrimSpace(text)
	if text == "" {
		return nil
	}
	return strings.Fields(text)
}

// Tokenize splits text into subword tokens using WordPiece.
func (t *BertWordPieceTokenizer) Tokenize(text string) []string {
	var outputTokens []string

	// Basic whitespace and punctuation split (simplified)
	words := t.whitespaceTokenize(text)

	t.mu.RLock()
	defer t.mu.RUnlock()

	for _, word := range words {
		chars := []rune(word)
		if len(chars) > t.maxInputCharsPerWord {
			outputTokens = append(outputTokens, t.unkToken)
			continue
		}

		isBad := false
		start := 0
		var subTokens []string

		for start < len(chars) {
			end := len(chars)
			var curStr string
			found := false

			for start < end {
				substr := string(chars[start:end])
				if start > 0 {
					substr = "##" + substr
				}

				if _, ok := t.vocab[substr]; ok {
					curStr = substr
					found = true
					break
				}
				end--
			}

			if !found {
				isBad = true
				break
			}

			subTokens = append(subTokens, curStr)
			start = end
		}

		if isBad {
			outputTokens = append(outputTokens, t.unkToken)
		} else {
			outputTokens = append(outputTokens, subTokens...)
		}
	}

	return outputTokens
}

func (t *BertWordPieceTokenizer) ConvertTokensToIds(tokens []string) []int {
	t.mu.RLock()
	defer t.mu.RUnlock()

	var ids []int
	for _, token := range tokens {
		if id, ok := t.vocab[token]; ok {
			ids = append(ids, id)
		} else {
			ids = append(ids, t.vocab[t.unkToken])
		}
	}
	return ids
}
