// @omni-layer Concurrency | @omni-source sidharthrajaram/StyleTTS2 | @omni-lang Go
// @omni-description TTS synthesis pipeline: concurrent multi-speaker voice
// synthesis with style transfer and mel-to-audio batch processing.
package ttssynth

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type SynthRequest struct {
	ID        string
	Text      string
	SpeakerID int
	Speed     float64
}

type SynthResult struct {
	ID         string
	Duration   float64
	MelFrames  int
	SampleRate int
}

type TTSSynthPipeline struct {
	mu         sync.Mutex
	workers    int
	sampleRate int
	completed  int
}

func NewTTSSynthPipeline(workers, sampleRate int) *TTSSynthPipeline {
	return &TTSSynthPipeline{workers: workers, sampleRate: sampleRate}
}

func (p *TTSSynthPipeline) textToPhonemes(text string) int {
	count := 0
	for _, ch := range text {
		if (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') {
			count++
		}
	}
	return count
}

func (p *TTSSynthPipeline) SynthesizeBatch(requests []SynthRequest) OmniResult[[]SynthResult] {
	results := make([]SynthResult, len(requests))
	var wg sync.WaitGroup
	sem := make(chan struct{}, p.workers)

	for i, req := range requests {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, r SynthRequest) {
			defer wg.Done()
			defer func() { <-sem }()
			nPhonemes := p.textToPhonemes(r.Text)
			speed := r.Speed
			if speed <= 0 {
				speed = 1.0
			}
			avgDurPerPhoneme := 80.0 / speed // ms
			totalDur := float64(nPhonemes) * avgDurPerPhoneme / 1000.0
			hopLength := 256
			melFrames := int(totalDur * float64(p.sampleRate) / float64(hopLength))
			if melFrames < 1 {
				melFrames = 1
			}
			// Apply speaker style variation
			styleOffset := math.Sin(float64(r.SpeakerID)*0.5) * 0.1
			totalDur += styleOffset
			if totalDur < 0.01 {
				totalDur = 0.01
			}

			results[idx] = SynthResult{
				ID:         r.ID,
				Duration:   totalDur,
				MelFrames:  melFrames,
				SampleRate: p.sampleRate,
			}
		}(i, req)
	}
	wg.Wait()

	p.mu.Lock()
	p.completed += len(requests)
	p.mu.Unlock()
	return OmniResult[[]SynthResult]{Data: results}
}

func (p *TTSSynthPipeline) Stats() string {
	p.mu.Lock()
	defer p.mu.Unlock()
	return fmt.Sprintf("completed=%d rate=%d", p.completed, p.sampleRate)
}
