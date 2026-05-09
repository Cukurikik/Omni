// Omni SimplyRetrieve RAG Gateway (Go)
// Ref: RCGAI/SimplyRetrieve — MIT
package network_gocore

import (
	"math"
	"sort"
	"strings"
)

type RetrievedDoc struct {
	ID    string  `json:"id"`
	Score float64 `json:"score"`
	Text  string  `json:"text"`
}

func BM25Score(tf, df, docLen int, avgDL float64, nDocs int, k1, b float64) float64 {
	idf := math.Log((float64(nDocs)-float64(df)+0.5)/(float64(df)+0.5) + 1.0)
	tfNorm := (float64(tf) * (k1 + 1.0)) / (float64(tf) + k1*(1.0-b+b*(float64(docLen)/avgDL)))
	return idf * tfNorm
}

func RetrieveTopK(query string, docs []RetrievedDoc, k int) []RetrievedDoc {
	qTokens := strings.Fields(strings.ToLower(query))
	for i := range docs {
		score := 0.0
		docLower := strings.ToLower(docs[i].Text)
		for _, t := range qTokens {
			if strings.Contains(docLower, t) {
				score += 1.0
			}
		}
		docs[i].Score = score / math.Max(float64(len(qTokens)), 1)
	}
	sort.Slice(docs, func(i, j int) bool { return docs[i].Score > docs[j].Score })
	if k > len(docs) {
		k = len(docs)
	}
	return docs[:k]
}

