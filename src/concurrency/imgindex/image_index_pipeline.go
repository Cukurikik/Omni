// @omni-layer Concurrency | @omni-source minimaxir/imgbeddings | @omni-lang Go
// @omni-description Image indexing pipeline: concurrent CLIP embedding
// computation with batch processing and search index building.
package imgindex

import (
	"fmt"
	"math"
	"sort"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type ImageEntry struct {
	ID        string
	Embedding []float64
}

type SearchResult struct {
	ID    string
	Score float64
}

type ImageIndexPipeline struct {
	mu      sync.RWMutex
	index   []ImageEntry
	dim     int
	workers int
}

func NewImageIndexPipeline(dim, workers int) *ImageIndexPipeline {
	return &ImageIndexPipeline{dim: dim, workers: workers}
}

func (p *ImageIndexPipeline) EmbedAndIndex(images []struct {
	ID       string
	Features []float64
}) OmniResult[int] {
	var wg sync.WaitGroup
	sem := make(chan struct{}, p.workers)
	entries := make([]ImageEntry, len(images))

	for i, img := range images {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, id string, feat []float64) {
			defer wg.Done()
			defer func() { <-sem }()
			emb := make([]float64, p.dim)
			for j := 0; j < len(feat) && j < p.dim; j++ {
				emb[j] = math.Tanh(feat[j] * 0.5)
			}
			norm := 0.0
			for _, v := range emb {
				norm += v * v
			}
			norm = math.Sqrt(norm + 1e-8)
			for j := range emb {
				emb[j] /= norm
			}
			entries[idx] = ImageEntry{ID: id, Embedding: emb}
		}(i, img.ID, img.Features)
	}
	wg.Wait()

	p.mu.Lock()
	p.index = append(p.index, entries...)
	total := len(p.index)
	p.mu.Unlock()
	return OmniResult[int]{Data: total}
}

func (p *ImageIndexPipeline) Search(query []float64, topK int) OmniResult[[]SearchResult] {
	p.mu.RLock()
	defer p.mu.RUnlock()

	type scored struct {
		id    string
		score float64
	}
	results := make([]scored, 0, len(p.index))
	for _, entry := range p.index {
		dot := 0.0
		d := p.dim
		if len(query) < d {
			d = len(query)
		}
		if len(entry.Embedding) < d {
			d = len(entry.Embedding)
		}
		for j := 0; j < d; j++ {
			dot += query[j] * entry.Embedding[j]
		}
		results = append(results, scored{id: entry.ID, score: dot})
	}
	sort.Slice(results, func(i, j int) bool { return results[i].score > results[j].score })
	if topK > len(results) {
		topK = len(results)
	}
	out := make([]SearchResult, topK)
	for i := 0; i < topK; i++ {
		out[i] = SearchResult{ID: results[i].id, Score: results[i].score}
	}
	return OmniResult[[]SearchResult]{Data: out}
}

func (p *ImageIndexPipeline) Size() int {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return len(p.index)
}

func (p *ImageIndexPipeline) Stats() string {
	return fmt.Sprintf("indexed=%d dim=%d", p.Size(), p.dim)
}
