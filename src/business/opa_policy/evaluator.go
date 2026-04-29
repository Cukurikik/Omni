package opapolicy

import "github.com/omni/core/result"

type Evaluator struct {}

func (e *Evaluator) EvaluatePolicy(input map[string]interface{}) result.Result[bool] {
	if input == nil {
		return result.Err[bool](result.NewError("Input cannot be nil"))
	}
	return result.Ok(true)
}
