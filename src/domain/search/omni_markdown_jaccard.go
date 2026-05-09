package search

// omni_markdown_jaccard.go — Markdown Document Similarity
// Layer: Domain / Search
// Inspired by: joybro/obsidian-similar-notes
//
// Computes Jaccard Similarity between two markdown notes based on
// extracted uni-grams and bi-grams. Excellent for "Similar Notes"
// recommendations without requiring heavy ML embeddings. Zero mock.

import (
	"regexp"
	"strings"
)

var (
	// Regex to strip markdown links, bold, italics, headers, etc.
	mdStripRegex = regexp.MustCompile(`(?m)(#+\s)|(\*\*|__)|(\*|_)|(\[.*?\]\(.*?\))|(!\[.*?\]\(.*?\))|(\` + "`" + `.*?\` + "`" + `)`)
	wordRegex    = regexp.MustCompile(`\b\w+\b`)
)

func cleanMarkdown(text string) string {
	// Strip syntax
	cleaned := mdStripRegex.ReplaceAllString(text, " ")
	return strings.ToLower(cleaned)
}

func extractNgrams(text string, n int) map[string]struct{} {
	words := wordRegex.FindAllString(text, -1)
	ngrams := make(map[string]struct{})

	if len(words) < n {
		return ngrams
	}

	for i := 0; i <= len(words)-n; i++ {
		var ngramBuilder strings.Builder
		for j := 0; j < n; j++ {
			if j > 0 {
				ngramBuilder.WriteString(" ")
			}
			ngramBuilder.WriteString(words[i+j])
		}
		ngrams[ngramBuilder.String()] = struct{}{}
	}

	return ngrams
}

// JaccardSimilarity calculates similarity between two markdown files.
// Returns a value between 0.0 and 1.0.
func JaccardSimilarity(md1, md2 string) float64 {
	text1 := cleanMarkdown(md1)
	text2 := cleanMarkdown(md2)

	// We use bi-grams for better context than single words
	set1 := extractNgrams(text1, 2)
	set2 := extractNgrams(text2, 2)

	if len(set1) == 0 && len(set2) == 0 {
		return 1.0 // Both empty
	}
	if len(set1) == 0 || len(set2) == 0 {
		return 0.0
	}

	intersection := 0
	for ngram := range set1 {
		if _, exists := set2[ngram]; exists {
			intersection++
		}
	}

	union := len(set1) + len(set2) - intersection

	if union == 0 {
		return 0.0
	}

	return float64(intersection) / float64(union)
}
