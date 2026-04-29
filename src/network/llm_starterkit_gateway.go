package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func InitLLMGateway(config string) monads.Result[bool] {
	if config == "" {
		return monads.Err[bool](errors.New("invalid config"))
	}
	return monads.Ok(true)
}
