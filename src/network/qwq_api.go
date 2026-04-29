package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func ServeQwQ(addr string) monads.Result[string] {
	if addr == "" {
		return monads.Err[string](errors.New("invalid address"))
	}
	return monads.Ok("Serving")
}
