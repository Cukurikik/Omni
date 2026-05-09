// @omni-layer Concurrency | @omni-source desaixie/zeroverse + yuanzhoulvpi2017/DocumentSearch | @omni-lang Go
// @omni-description Document chunking pipeline: concurrent document ingestion
// with parallel chunk splitting, embedding, and index building.
package dochunk

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type Chunk struct {
	DocID     string
	ChunkIdx  int
	Text      string
	Embedding []float64
}

type ChunkingPipeline struct {
	mu          sync.Mutex
	workers     int
	chunkSize   int
	overlap     int
	dim         int
	totalChunks int
	chunks      []Chunk
}

func NewChunkingPipeline(workers, chunkSize, overlap, dim int) *ChunkingPipeline {
	return &ChunkingPipeline{
		workers: workers, chunkSize: chunkSize,
		overlap: overlap, dim: dim,
	}
}

func (p *ChunkingPipeline) embed(text string) []float64 {
	emb := make([]float64, p.dim)
	for i, ch := range text {
		if i >= 300 {
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

func (p *ChunkingPipeline) IngestDocuments(docs []struct{ ID, Text string }) OmniResult[int] {
	var allChunks []Chunk
	var wg sync.WaitGroup
	var chunkMu sync.Mutex
	sem := make(chan struct{}, p.workers)

	for _, doc := range docs {
		wg.Add(1)
		sem <- struct{}{}
		go func(id, text string) {
			defer wg.Done()
			defer func() { <-sem }()
			var docChunks []Chunk
			start := 0
			idx := 0
			for start < len(text) {
				end := start + p.chunkSize
				if end > len(text) {
					end = len(text)
				}
				chunkText := text[start:end]
				emb := p.embed(chunkText)
				docChunks = append(docChunks, Chunk{
					DocID: id, ChunkIdx: idx,
					Text: chunkText, Embedding: emb,
				})
				start += p.chunkSize - p.overlap
				idx++
			}
			chunkMu.Lock()
			allChunks = append(allChunks, docChunks...)
			chunkMu.Unlock()
		}(doc.ID, doc.Text)
	}
	wg.Wait()

	p.mu.Lock()
	p.chunks = append(p.chunks, allChunks...)
	p.totalChunks += len(allChunks)
	p.mu.Unlock()
	return OmniResult[int]{Data: len(allChunks)}
}

func (p *ChunkingPipeline) Search(query string, topK int) OmniResult[[]Chunk] {
	qEmb := p.embed(query)
	p.mu.Lock()
	defer p.mu.Unlock()

	type scored struct {
		chunk Chunk
		score float64
	}
	var results []scored
	for _, c := range p.chunks {
		dot := 0.0
		d := p.dim
		if len(c.Embedding) < d {
			d = len(c.Embedding)
		}
		for j := 0; j < d; j++ {
			dot += qEmb[j] * c.Embedding[j]
		}
		results = append(results, scored{chunk: c, score: dot})
	}
	// Sort by score descending
	for i := 0; i < len(results)-1; i++ {
		for j := i + 1; j < len(results); j++ {
			if results[j].score > results[i].score {
				results[i], results[j] = results[j], results[i]
			}
		}
	}
	if topK > len(results) {
		topK = len(results)
	}
	out := make([]Chunk, topK)
	for i := 0; i < topK; i++ {
		out[i] = results[i].chunk
	}
	return OmniResult[[]Chunk]{Data: out}
}

func (p *ChunkingPipeline) Stats() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	return fmt.Sprintf("chunks=%d", p.totalChunks)
}
