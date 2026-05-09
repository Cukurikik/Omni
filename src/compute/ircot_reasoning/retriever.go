package ircot

import "omni-engines/core/result"

type Retriever struct{}

func (r *Retriever) Fetch(query string) result.Result[string] {
	if query == "" {
		return result.Err[string](result.NewError("Empty query"))
	}
	return result.Ok("Retrieved context based on query")
}
