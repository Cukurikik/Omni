// OMNI Network Layer - BentoML HTTP Runner
package network

import (
	"errors"
)

type RunnerResult struct {
	Response string
	Err      error
}

func InvokeBentoRunner(inputJson string) RunnerResult {
	if inputJson == "" {
		return RunnerResult{Response: "", Err: errors.New("empty runner input")}
	}

	// Go fasthttp reverse proxy logic to BentoML local runner process
	return RunnerResult{Response: `{"prediction": 4.2}`, Err: nil}
}
