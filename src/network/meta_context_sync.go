package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func SyncEvolution(version int) monads.Result[bool] {
	if version < 0 {
		return monads.Err[bool](errors.New("invalid version"))
	}
	return monads.Ok(true)
}
