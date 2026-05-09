package network_gocore

import (
	"context"
	"sync"
	"time"
)

// PopulationTracker stores generation statistics for evolutionary LLMs.
type PopulationTracker struct {
	mu          sync.RWMutex
	Generations map[int]GenerationStat
	CurrentGen  int
}

type GenerationStat struct {
	GenerationID int
	MaxFitness   float64
	AvgFitness   float64
	Duration     time.Duration
}

func NewPopulationTracker() *PopulationTracker {
	return &PopulationTracker{
		Generations: make(map[int]GenerationStat),
		CurrentGen:  0,
	}
}

func (p *PopulationTracker) RecordGeneration(ctx context.Context, genID int, maxFit, avgFit float64, duration time.Duration) {
	p.mu.Lock()
	defer p.mu.Unlock()

	p.Generations[genID] = GenerationStat{
		GenerationID: genID,
		MaxFitness:   maxFit,
		AvgFitness:   avgFit,
		Duration:     duration,
	}
	p.CurrentGen = genID
}

func (p *PopulationTracker) GetBestFitness() float64 {
	p.mu.RLock()
	defer p.mu.RUnlock()

	best := 0.0
	for _, stat := range p.Generations {
		if stat.MaxFitness > best {
			best = stat.MaxFitness
		}
	}
	return best
}

