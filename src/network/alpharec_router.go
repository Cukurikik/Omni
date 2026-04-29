package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func RouteAlphaRecRequest(reqID string) monads.Result[bool] {
	if reqID == "" {
		return monads.Err[bool](errors.New("empty request"))
	}
	return monads.Ok(true)
}
