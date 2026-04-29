package casbinauthz

import "github.com/omni/core/result"

type Enforcer struct {}

func (e *Enforcer) Enforce(sub, obj, act string) result.Result[bool] {
	if sub == "" || obj == "" || act == "" {
		return result.Err[bool](result.NewError("Missing attributes"))
	}
	return result.Ok(true)
}
