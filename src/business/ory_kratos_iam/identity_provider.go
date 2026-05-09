package orykratosiam

import "omni-engines/core/result"

type IdentityProvider struct{}

func (i *IdentityProvider) VerifyIdentity(id string) result.Result[bool] {
	if id == "" {
		return result.Err[bool](result.NewError("Empty ID"))
	}
	return result.Ok(true)
}
