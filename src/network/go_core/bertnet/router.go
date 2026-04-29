package bertnet

import (
	"context"
	"errors"
)

type HarvestResult struct {
	Similarity float64
	Merged     bool
}

type HarvestRouter struct {
	MergeThreshold float64
}

// OMNI Network Layer - Harvest Router
func (r *HarvestRouter) RouteHarvest(ctx context.Context, jaccard float64) (*HarvestResult, error) {
	if jaccard < 0.0 || jaccard > 1.0 {
		return nil, errors.New("jaccard similarity out of bounds")
	}
	
	return &HarvestResult{
		Similarity: jaccard,
		Merged:     jaccard >= r.MergeThreshold,
	}, nil
}
