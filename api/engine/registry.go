package engine

import (
	"fmt"
	"omnitools/core"
	"omnitools/services"
)

// ExecuteTool adalah Switchboard utama yang dihasilkan otomatis oleh OMNI-SYNC.
// JANGAN EDIT FILE INI SECARA MANUAL!
func ExecuteTool(job *core.Job) ([]byte, error) {
	switch job.ID {
	case "demo_tool":
		return services.ExecuteEngineWithTimeout(job.EngineCmd, job.Args, job.Timeout)
	default:
		return nil, fmt.Errorf("tool_id [%s] tidak terdaftar di engine registry", job.ID)
	}
}
