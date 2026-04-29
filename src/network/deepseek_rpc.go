package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func ServeDeepseekRPC(port int) monads.Result[bool] {
	if port <= 0 {
		return monads.Err[bool](errors.New("invalid port"))
	}
	return monads.Ok(true)
}
