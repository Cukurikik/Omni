package scilm

import "errors"

type OmniResult struct {
	Value interface{}
	Error error
}

func QueueReview(paperId string) OmniResult {
	if paperId == "" {
		return OmniResult{Value: nil, Error: errors.New("Invalid paper ID")}
	}

	// Go routines for async peer review queuing
	return OmniResult{Value: "Queued", Error: nil}
}
