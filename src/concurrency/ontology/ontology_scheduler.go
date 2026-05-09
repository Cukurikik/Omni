// @omni-layer Concurrency | @omni-source HamedBabaei/LLMs4OL | @omni-lang Go
// @omni-description Ontology pipeline scheduler: concurrent term typing,
// taxonomy discovery, and relation extraction with worker pool.
package ontology

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type TermType struct {
	Term       string
	Type       string
	Confidence float64
}

type TaxonomyEdge struct {
	Child  string
	Parent string
	Score  float64
}

type OntologyScheduler struct {
	workers int
	mu      sync.Mutex
	types   []TermType
	edges   []TaxonomyEdge
}

func NewOntologyScheduler(workers int) *OntologyScheduler {
	return &OntologyScheduler{workers: workers}
}

func hashEmbed(text string, dim int) []float64 {
	emb := make([]float64, dim)
	for i, ch := range text {
		idx := (int(ch) * (i + 1)) % dim
		emb[idx] += math.Sin(float64(ch)*0.1) * 0.1
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

func (s *OntologyScheduler) ProcessTerms(terms []string) OmniResult[[]TermType] {
	results := make([]TermType, len(terms))
	var wg sync.WaitGroup
	sem := make(chan struct{}, s.workers)

	conceptTypes := []string{"entity", "process", "attribute", "relation", "event"}
	dim := 128

	for i, term := range terms {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, t string) {
			defer wg.Done()
			defer func() { <-sem }()
			emb := hashEmbed(t, dim)
			bestType := ""
			bestScore := -1.0
			for _, ct := range conceptTypes {
				ctEmb := hashEmbed(ct, dim)
				dot := 0.0
				for j := 0; j < dim; j++ {
					dot += emb[j] * ctEmb[j]
				}
				score := (dot + 1) / 2
				if score > bestScore {
					bestScore = score
					bestType = ct
				}
			}
			results[idx] = TermType{Term: t, Type: bestType, Confidence: bestScore}
		}(i, term)
	}
	wg.Wait()
	s.mu.Lock()
	s.types = append(s.types, results...)
	s.mu.Unlock()
	return OmniResult[[]TermType]{Data: results}
}

func (s *OntologyScheduler) DiscoverTaxonomy(terms []string) OmniResult[[]TaxonomyEdge] {
	var edges []TaxonomyEdge
	dim := 128
	for i, child := range terms {
		childEmb := hashEmbed(child, dim)
		bestParent := ""
		bestScore := -1.0
		for j, parent := range terms {
			if i == j {
				continue
			}
			parentEmb := hashEmbed(parent, dim)
			dot := 0.0
			for k := 0; k < dim; k++ {
				dot += childEmb[k] * parentEmb[k]
			}
			score := (dot + 1) / 2
			if score > bestScore {
				bestScore = score
				bestParent = parent
			}
		}
		if bestParent != "" {
			edges = append(edges, TaxonomyEdge{Child: child, Parent: bestParent, Score: bestScore})
		}
	}
	s.mu.Lock()
	s.edges = append(s.edges, edges...)
	s.mu.Unlock()
	return OmniResult[[]TaxonomyEdge]{Data: edges}
}

func (s *OntologyScheduler) Stats() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	return fmt.Sprintf("types=%d edges=%d", len(s.types), len(s.edges))
}
