package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func StartOpenGPTServer(port int) monads.Result[string] {
	if port <= 0 || port > 65535 {
		return monads.Err[string](errors.New("invalid port"))
	}
	return monads.Ok("Server started")
}
