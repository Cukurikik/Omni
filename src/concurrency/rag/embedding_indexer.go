// @omni-layer Concurrency | @omni-source run-llama/llama_index | @omni-lang Go
// @omni-description RAG embedding indexer: concurrent document embedding and
// vector index building with parallel chunk processing.
package rag

import (
	"math"
	"sync"
	"sync/atomic"
)

type Document struct {
	ID   string
	Text string
	Emb  []float64
}

type IndexBuilder struct {
	d        int
	nWorkers int
	docs     []Document
	mu       sync.RWMutex
	indexed  int64
}

func NewIndexBuilder(d, nWorkers int) *IndexBuilder {
	return &IndexBuilder{d: d, nWorkers: nWorkers}
}

func (b *IndexBuilder) hashEmbed(text string) []float64 {
	emb := make([]float64, b.d)
	for i := 0; i < b.d; i++ {
		h := 0.0
		for c := 0; c < len(text) && c < 100; c++ {
			h += float64(text[c]) * math.Sin(float64(i+1)*float64(c+1)*0.001)
		}
		emb[i] = math.Tanh(h * 0.001)
	}
	return emb
}

func (b *IndexBuilder) BuildIndex(docs []Document) {
	ch := make(chan int, len(docs))
	for i := range docs {
		ch <- i
	}
	close(ch)
	var wg sync.WaitGroup
	for w := 0; w < b.nWorkers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for idx := range ch {
				docs[idx].Emb = b.hashEmbed(docs[idx].Text)
				atomic.AddInt64(&b.indexed, 1)
			}
		}()
	}
	wg.Wait()
	b.mu.Lock()
	b.docs = append(b.docs, docs...)
	b.mu.Unlock()
}

func (b *IndexBuilder) Search(query []float64, topK int) []Document {
	b.mu.RLock()
	defer b.mu.RUnlock()
	type scored struct {
		doc   Document
		score float64
	}
	results := make([]scored, len(b.docs))
	for i, doc := range b.docs {
		dot, na, nb := 0.0, 0.0, 0.0
		d := len(query)
		if len(doc.Emb) < d {
			d = len(doc.Emb)
		}
		for j := 0; j < d; j++ {
			dot += query[j] * doc.Emb[j]
			na += query[j] * query[j]
			nb += doc.Emb[j] * doc.Emb[j]
		}
		results[i] = scored{doc, dot / (math.Sqrt(na)*math.Sqrt(nb) + 1e-8)}
	}
	for i := 0; i < len(results)-1; i++ {
		for j := i + 1; j < len(results); j++ {
			if results[j].score > results[i].score {
				results[i], results[j] = results[j], results[i]
			}
		}
	}
	out := make([]Document, 0, topK)
	for i := 0; i < topK && i < len(results); i++ {
		out = append(out, results[i].doc)
	}
	return out
}
