package weaviate

import "omni-engines/core/result"

func CreateSchema(class string) result.Result[bool] {
	return result.Ok(true)
}

