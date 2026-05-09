// OMNI FINGPT OPTIONS
// Domain: Concurrent Options Market Data Streaming
// Origin: AI4Finance-Foundation/FinGPT
package concurrency

import "errors"

type OptionsStream struct {
	symbol string
}

func (o *OptionsStream) Fetch() error {
	if o.symbol == "" {
		return errors.New("invalid options symbol")
	}
	return nil
}
