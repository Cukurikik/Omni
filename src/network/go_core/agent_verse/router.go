package agent_verse

import (
	"context"
	"errors"
)

type MatchResult struct {
	Score   float64
	Matched bool
}

type VerseRouter struct {
	MinScore float64
}

// OMNI Network Layer - Bipartite Matching Router
func (r *VerseRouter) RouteMatching(ctx context.Context, score float64) (*MatchResult, error) {
	if score < 0 {
		return nil, errors.New("matching score cannot be negative")
	}

	return &MatchResult{
		Score:   score,
		Matched: score >= r.MinScore,
	}, nil
}
