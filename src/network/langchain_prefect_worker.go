package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func StartWorker(queue string) monads.Result[string] {
	if queue == "" {
		return monads.Err[string](errors.New("queue missing"))
	}
	return monads.Ok("Worker started")
}
