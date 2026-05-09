package llm_table_survey

import (
	"bytes"
	"context"
	"errors"
)

type SurveyResult struct {
	DelimiterCount int32
	Valid          bool
}

type SurveyRouter struct {
	Delimiter byte
}

func NewSurveyRouter(delim byte) *SurveyRouter {
	return &SurveyRouter{Delimiter: delim}
}

// OMNI Network Layer - Table validation and parsing
func (r *SurveyRouter) ProcessTable(ctx context.Context, payload []byte) (*SurveyResult, error) {
	if len(payload) == 0 {
		return nil, errors.New("empty table payload")
	}

	// Direct byte-level counting fallback (C++ kernel binding point)
	count := int32(bytes.Count(payload, []byte{r.Delimiter}))

	return &SurveyResult{
		DelimiterCount: count,
		Valid:          count > 0,
	}, nil
}
