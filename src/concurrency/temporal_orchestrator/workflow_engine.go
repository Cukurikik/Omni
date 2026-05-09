package temporalorchestrator

import "omni-engines/core/result"

type WorkflowEngine struct {
	activeWorkflows int
}

func (w *WorkflowEngine) StartWorkflow(id string) result.Result[bool] {
	if id == "" {
		return result.Err[bool](result.NewError("ID empty"))
	}
	w.activeWorkflows++
	return result.Ok(true)
}
