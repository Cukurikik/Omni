package telepathy

import (
	"context"

	"omnitools/engine/singularity"
)

// RoutesSingularity menghubungkan OMNI Engine ke Jaringan Telepathy (Phase 20).
func RoutesSingularity(ctx context.Context, method string, args map[string]interface{}, ok func(interface{}) OmniResponse, fail func(error) OmniResponse) (OmniResponse, bool) {
	kernel := singularity.IgniteSingularity()

	switch method {
	case "omni::Singularity::GetDiagnostics":
		return ok(kernel.GetDiagnostics()), true

	case "omni::Singularity::EnsurePhases":
		err := kernel.EnsurePhases(ctx)
		if err != nil {
			return fail(err), true
		}
		return ok("All Phases Active"), true

	case "omni::Singularity::JITOptimize":
		astPayload, _ := args["ast_buffer"].(string)
		result := kernel.ProcessNeuralJIT(astPayload)
		return ok(result), true
	}

	return OmniResponse{}, false
}
