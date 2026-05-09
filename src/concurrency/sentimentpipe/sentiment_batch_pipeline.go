// @omni-layer Concurrency | @omni-source TheophileBlard/french-sentiment | @omni-lang Go
// @omni-description Sentiment batch pipeline: concurrent multilingual sentiment
// analysis with language detection and aggregation.
package sentimentpipe

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type SentimentItem struct {
	Text       string
	Language   string
	Label      string
	Confidence float64
}

type SentimentBatchPipeline struct {
	mu       sync.Mutex
	workers  int
	dim      int
	analyzed int
}

func NewSentimentBatchPipeline(workers, dim int) *SentimentBatchPipeline {
	return &SentimentBatchPipeline{workers: workers, dim: dim}
}

func detectLanguage(text string) string {
	langs := map[string][]string{
		"fr": {"le", "la", "de", "des", "est", "une", "les", "pas", "que"},
		"de": {"der", "die", "das", "und", "ist", "ein", "nicht"},
		"es": {"el", "la", "de", "que", "es", "los", "una"},
		"en": {"the", "is", "are", "was", "have", "has", "not"},
	}
	bestLang := "en"
	bestScore := 0
	words := make(map[string]bool)
	for _, ch := range text {
		if ch == ' ' {
			continue
		}
	}
	_ = words
	for lang, markers := range langs {
		score := 0
		for _, marker := range markers {
			for i := 0; i+len(marker) <= len(text); i++ {
				if text[i:i+len(marker)] == marker {
					score++
				}
			}
		}
		if score > bestScore {
			bestScore = score
			bestLang = lang
		}
	}
	return bestLang
}

func (p *SentimentBatchPipeline) AnalyzeBatch(texts []string) OmniResult[[]SentimentItem] {
	results := make([]SentimentItem, len(texts))
	var wg sync.WaitGroup
	sem := make(chan struct{}, p.workers)
	labels := []string{"very_negative", "negative", "neutral", "positive", "very_positive"}

	for i, text := range texts {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, t string) {
			defer wg.Done()
			defer func() { <-sem }()
			lang := detectLanguage(t)
			// Compute embedding-based scores
			logits := make([]float64, len(labels))
			for c := range logits {
				score := 0.0
				for j, ch := range t {
					if j >= 100 {
						break
					}
					score += math.Sin(float64(ch)*float64(c+1)*0.001) * 0.01
				}
				logits[c] = score
			}
			maxL := logits[0]
			for _, l := range logits {
				if l > maxL {
					maxL = l
				}
			}
			total := 0.0
			for j := range logits {
				logits[j] = math.Exp(logits[j] - maxL)
				total += logits[j]
			}
			bestIdx := 0
			bestConf := 0.0
			for j := range logits {
				prob := logits[j] / total
				if prob > bestConf {
					bestConf = prob
					bestIdx = j
				}
			}
			results[idx] = SentimentItem{
				Text: t, Language: lang,
				Label: labels[bestIdx], Confidence: bestConf,
			}
		}(i, text)
	}
	wg.Wait()

	p.mu.Lock()
	p.analyzed += len(texts)
	p.mu.Unlock()
	return OmniResult[[]SentimentItem]{Data: results}
}

func (p *SentimentBatchPipeline) Stats() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	return fmt.Sprintf("analyzed=%d workers=%d", p.analyzed, p.workers)
}
