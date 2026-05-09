package temporal

import "omni-engines/core/result"

func ExecuteWorkflow(name string) result.Result[bool] {
	return result.Ok(true)
}

