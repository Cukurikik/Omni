package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func RouteMistralQuery(q string) monads.Result[string] {
	if q == "" {
		return monads.Err[string](errors.New("empty query"))
	}
	return monads.Ok("Routed")
}
