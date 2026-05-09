package mistral_haystack

import (
	"context"

	"omni-engines/core/result"
)

type Document struct {
	Content string
	Meta    map[string]string
}

func ProcessHaystackNode(ctx context.Context, docs []Document) result.Result[[]Document] {
	if len(docs) == 0 {
		return result.Err[[]Document](nil)
	}
	return result.Ok(docs)
}
