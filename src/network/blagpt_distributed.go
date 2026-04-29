package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func InitDistributedBlaGPT(nodes int) monads.Result[bool] {
	if nodes <= 0 {
		return monads.Err[bool](errors.New("nodes must be positive"))
	}
	return monads.Ok(true)
}
