// @omni-layer Concurrency | @omni-source calebevans/cordon | @omni-lang Go
// @omni-description Log ingestion pipeline: high-throughput concurrent log
// line processing with anomaly detection and template extraction.
package logpipeline

import (
	"fmt"
	"math"
	"regexp"
	"strings"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type LogEntry struct {
	Line      string
	Template  string
	IsAnomaly bool
	Distance  float64
}

type LogIngestionPipeline struct {
	mu        sync.Mutex
	workers   int
	threshold float64
	templates map[string]int
	centroid  []float64
	nSeen     int
	dim       int
}

var ipRegex = regexp.MustCompile(`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`)
var tsRegex = regexp.MustCompile(`\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}`)
var numRegex = regexp.MustCompile(`\b\d+\b`)

func NewLogIngestionPipeline(workers int, threshold float64) *LogIngestionPipeline {
	dim := 64
	return &LogIngestionPipeline{
		workers: workers, threshold: threshold,
		templates: make(map[string]int),
		centroid:  make([]float64, dim), dim: dim,
	}
}

func tokenizeLog(line string) string {
	line = ipRegex.ReplaceAllString(line, "<IP>")
	line = tsRegex.ReplaceAllString(line, "<TS>")
	line = numRegex.ReplaceAllString(line, "<N>")
	return strings.TrimSpace(line)
}

func embedLog(text string, dim int) []float64 {
	emb := make([]float64, dim)
	for i, ch := range text {
		if i >= 200 {
			break
		}
		idx := (int(ch) * (i + 1)) % dim
		emb[idx] += math.Sin(float64(ch) * 0.05)
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

func (p *LogIngestionPipeline) ProcessBatch(lines []string) OmniResult[[]LogEntry] {
	results := make([]LogEntry, len(lines))
	var wg sync.WaitGroup
	sem := make(chan struct{}, p.workers)

	for i, line := range lines {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, l string) {
			defer wg.Done()
			defer func() { <-sem }()
			template := tokenizeLog(l)
			emb := embedLog(template, p.dim)

			p.mu.Lock()
			p.templates[template]++
			if p.nSeen == 0 {
				copy(p.centroid, emb)
			} else {
				for j := range p.centroid {
					p.centroid[j] = (p.centroid[j]*float64(p.nSeen) + emb[j]) / float64(p.nSeen+1)
				}
			}
			p.nSeen++
			dist := 0.0
			for j := range emb {
				d := emb[j] - p.centroid[j]
				dist += d * d
			}
			dist = math.Sqrt(dist)
			p.mu.Unlock()

			results[idx] = LogEntry{
				Line: l, Template: template,
				IsAnomaly: dist > p.threshold, Distance: dist,
			}
		}(i, line)
	}
	wg.Wait()
	return OmniResult[[]LogEntry]{Data: results}
}

func (p *LogIngestionPipeline) Stats() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	return fmt.Sprintf("seen=%d templates=%d", p.nSeen, len(p.templates))
}
