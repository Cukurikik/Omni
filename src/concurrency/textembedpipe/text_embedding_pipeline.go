// @omni-layer Concurrency | @omni-source OscarKjell/text | @omni-lang Go
// @omni-description Text embedding pipeline: concurrent text-to-embedding
// batch processor with pooling strategies and caching.
package textembedpipe

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type EmbeddingResult struct {
	Text      string
	Embedding []float64
	Norm      float64
}

type TextEmbeddingPipeline struct {
	mu        sync.Mutex
	workers   int
	dim       int
	cache     map[string][]float64
	processed int
}

func NewTextEmbeddingPipeline(workers, dim int) *TextEmbeddingPipeline {
	return &TextEmbeddingPipeline{
		workers: workers, dim: dim,
		cache: make(map[string][]float64),
	}
}

func (p *TextEmbeddingPipeline) embed(text string) []float64 {
	emb := make([]float64, p.dim)
	for i, ch := range text {
		if i >= 200 {
			break
		}
		idx := (int(ch) * (i + 1)) % p.dim
		emb[idx] += math.Tanh(float64(ch) * 0.01)
	}
	norm := 0.0
	for _, v := range emb {
		norm += v * v
	}
	norm = math.Sqrt(norm + 1e-8)
	for i := range emb {
		emb[i] /= norm
	}
	return emb
}

func (p *TextEmbeddingPipeline) EmbedBatch(texts []string) OmniResult[[]EmbeddingResult] {
	results := make([]EmbeddingResult, len(texts))
	var wg sync.WaitGroup
	sem := make(chan struct{}, p.workers)

	for i, text := range texts {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, t string) {
			defer wg.Done()
			defer func() { <-sem }()
			// Check cache
			p.mu.Lock()
			cached, ok := p.cache[t]
			p.mu.Unlock()
			var emb []float64
			if ok {
				emb = cached
			} else {
				emb = p.embed(t)
				p.mu.Lock()
				p.cache[t] = emb
				p.mu.Unlock()
			}
			norm := 0.0
			for _, v := range emb {
				norm += v * v
			}
			results[idx] = EmbeddingResult{Text: t, Embedding: emb, Norm: math.Sqrt(norm)}
		}(i, text)
	}
	wg.Wait()

	p.mu.Lock()
	p.processed += len(texts)
	p.mu.Unlock()
	return OmniResult[[]EmbeddingResult]{Data: results}
}

func (p *TextEmbeddingPipeline) CosineSimilarity(a, b []float64) float64 {
	d := len(a)
	if len(b) < d {
		d = len(b)
	}
	dot := 0.0
	na := 0.0
	nb := 0.0
	for i := 0; i < d; i++ {
		dot += a[i] * b[i]
		na += a[i] * a[i]
		nb += b[i] * b[i]
	}
	return dot / (math.Sqrt(na)*math.Sqrt(nb) + 1e-8)
}

func (p *TextEmbeddingPipeline) Stats() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	return fmt.Sprintf("processed=%d cached=%d", p.processed, len(p.cache))
}
