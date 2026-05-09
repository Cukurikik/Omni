// OmniPaperIndexer.go — Concurrent Research Paper Indexer
// Inspired by: nlp-papers & EMNLP-2023-Papers collections
// Layer: Domain / Go
//
// High-throughput concurrent pipeline for parsing, chunking, embedding,
// and indexing large collections of research papers into a vector database.

package knowledge_base

import (
	"context"
	"fmt"
	"log"
	"strings"
	"sync"
)

type Paper struct {
	ID       string
	Title    string
	Abstract string
	Content  string
	Year     int
	Authors  []string
}

type Chunk struct {
	PaperID string
	ChunkID int
	Text    string
	Vector  []float32
}

// Interfaces for dependencies
type TextExtractor interface {
	ExtractText(ctx context.Context, uri string) (*Paper, error)
}

type Embedder interface {
	Embed(ctx context.Context, texts []string) ([][]float32, error)
}

type VectorStore interface {
	Upsert(ctx context.Context, chunks []Chunk) error
}

type IndexingPipeline struct {
	extractor   TextExtractor
	embedder    Embedder
	vectorStore VectorStore
	chunkSize   int
	overlap     int
}

func NewIndexingPipeline(ext TextExtractor, emb Embedder, vs VectorStore) *IndexingPipeline {
	return &IndexingPipeline{
		extractor:   ext,
		embedder:    emb,
		vectorStore: vs,
		chunkSize:   512,
		overlap:     50,
	}
}

// ProcessBatch concurrently processes a batch of paper URIs.
func (p *IndexingPipeline) ProcessBatch(ctx context.Context, uris []string, concurrency int) error {
	uriChan := make(chan string, len(uris))
	paperChan := make(chan *Paper, concurrency*2)
	chunkChan := make(chan []Chunk, concurrency*2)

	var wgExtract sync.WaitGroup
	var wgEmbed sync.WaitGroup

	// Start extractors
	for i := 0; i < concurrency; i++ {
		wgExtract.Add(1)
		go func() {
			defer wgExtract.Done()
			for uri := range uriChan {
				paper, err := p.extractor.ExtractText(ctx, uri)
				if err != nil {
					log.Printf("Extraction failed for %s: %v", uri, err)
					continue
				}
				paperChan <- paper
			}
		}()
	}

	// Start embedders & chunkers
	for i := 0; i < concurrency; i++ {
		wgEmbed.Add(1)
		go func() {
			defer wgEmbed.Done()
			for paper := range paperChan {
				chunks := p.chunkText(paper)
				if len(chunks) == 0 {
					continue
				}

				texts := make([]string, len(chunks))
				for j, c := range chunks {
					texts[j] = c.Text
				}

				// Generate embeddings in batch
				vectors, err := p.embedder.Embed(ctx, texts)
				if err != nil {
					log.Printf("Embedding failed for paper %s: %v", paper.ID, err)
					continue
				}

				for j := range chunks {
					chunks[j].Vector = vectors[j]
				}

				chunkChan <- chunks
			}
		}()
	}

	// Start indexing
	errChan := make(chan error, 1)
	go func() {
		for chunks := range chunkChan {
			// Backoff/retry logic would go here
			if err := p.vectorStore.Upsert(ctx, chunks); err != nil {
				log.Printf("Failed to index chunks for paper %s: %v", chunks[0].PaperID, err)
			}
		}
		errChan <- nil
	}()

	// Feed URIs
	for _, uri := range uris {
		uriChan <- uri
	}
	close(uriChan)

	// Wait for extraction to finish
	wgExtract.Wait()
	close(paperChan)

	// Wait for embedding to finish
	wgEmbed.Wait()
	close(chunkChan)

	// Wait for indexing to finish
	<-errChan
	return nil
}

// chunkText splits paper content into overlapping windows.
func (p *IndexingPipeline) chunkText(paper *Paper) []Chunk {
	words := strings.Fields(paper.Content)
	var chunks []Chunk

	if len(words) == 0 {
		return chunks
	}

	chunkID := 0
	for i := 0; i < len(words); i += (p.chunkSize - p.overlap) {
		end := i + p.chunkSize
		if end > len(words) {
			end = len(words)
		}

		text := strings.Join(words[i:end], " ")
		chunks = append(chunks, Chunk{
			PaperID: paper.ID,
			ChunkID: chunkID,
			Text:    fmt.Sprintf("Title: %s\n\n%s", paper.Title, text),
		})
		chunkID++

		if end == len(words) {
			break
		}
	}

	return chunks
}
