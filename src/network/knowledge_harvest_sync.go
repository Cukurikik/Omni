package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func SyncKnowledge(node string) monads.Result[bool] {
	if node == "" {
		return monads.Err[bool](errors.New("invalid node"))
	}
	return monads.Ok(true)
}
