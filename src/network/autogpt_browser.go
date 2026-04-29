package network

import (
	"errors"
	"github.com/omni/core/monads"
)

func BrowseURL(url string) monads.Result[string] {
	if url == "" {
		return monads.Err[string](errors.New("empty url"))
	}
	return monads.Ok("Browsed")
}
