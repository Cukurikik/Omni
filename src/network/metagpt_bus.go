package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func PublishMessage(msg string) monads.Result[bool] {
	if msg == "" {
		return monads.Err[bool](errors.New("empty msg"))
	}
	return monads.Ok(true)
}
