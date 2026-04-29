package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func CallRAGAPI(endpoint string) monads.Result[string] {
	if endpoint == "" {
		return monads.Err[string](errors.New("empty endpoint"))
	}
	return monads.Ok("Success")
}
