// moe_gollemer_tagger.go — Domain / Inference
// Layer: Domain / NLP — Gollemer NLP Tagger & Expert Router
//
// Inspired by `golangast/gollemer`.
// Instead of using the heavyweight LLM itself to route queries, this Go module
// uses an extremely fast, classical NLP tagger to analyze the syntax and semantic
// intent of the user's prompt to pre-route them to the correct MoE Expert.

package moe

import (
	"fmt"
	"strings"
)

type TokenTag struct {
	Word string
	POS  string // Part of Speech (Noun, Verb, etc.)
}

type GollemerTagger struct {
	vocab map[string]string
}

func NewGollemerTagger() *GollemerTagger {
	fmt.Println("[Gollemer] Initialized Fast NLP POS Tagger for MoE Pre-Routing.")

	// A highly simplified mock vocabulary mapping for the tagger
	vocab := map[string]string{
		"def":     "KEYWORD_CODE",
		"func":    "KEYWORD_CODE",
		"class":   "KEYWORD_CODE",
		"symptom": "NOUN_MEDICAL",
		"doctor":  "NOUN_MEDICAL",
		"law":     "NOUN_LEGAL",
		"court":   "NOUN_LEGAL",
	}

	return &GollemerTagger{vocab: vocab}
}

// Tag analyzes the sentence and assigns POS tags
func (g *GollemerTagger) Tag(sentence string) []TokenTag {
	words := strings.Fields(strings.ToLower(sentence))
	tags := make([]TokenTag, len(words))

	for i, word := range words {
		pos, exists := g.vocab[word]
		if !exists {
			pos = "UNKNOWN"
		}
		tags[i] = TokenTag{Word: word, POS: pos}
	}

	return tags
}

// PredictExpert makes an O(1) decision on which MoE expert should handle the query
func (g *GollemerTagger) PredictExpert(sentence string) int {
	tags := g.Tag(sentence)

	scores := map[int]int{
		0: 0, // General
		1: 0, // Code
		2: 0, // Medical
		3: 0, // Legal
	}

	for _, t := range tags {
		switch t.POS {
		case "KEYWORD_CODE":
			scores[1] += 2
		case "NOUN_MEDICAL":
			scores[2] += 2
		case "NOUN_LEGAL":
			scores[3] += 2
		}
	}

	// Find max score
	bestExpert := 0
	maxScore := 0
	for expert, score := range scores {
		if score > maxScore {
			maxScore = score
			bestExpert = expert
		}
	}

	return bestExpert
}
