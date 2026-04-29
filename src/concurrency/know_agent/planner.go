package knowagent

import "github.com/omni/core/result"

type Planner struct {}

func (p *Planner) CreatePlan(goal string) result.Result[[]string] {
	if goal == "" {
		return result.Err[[]string](result.NewError("Goal is required"))
	}
	return result.Ok([]string{"Step 1", "Step 2"})
}
