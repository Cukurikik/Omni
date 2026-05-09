package temporal

import "omni-engines/core/result"

func RegisterActivity(name string) result.Result[bool] {
	return result.Ok(true)
}

