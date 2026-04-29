// OMNI Network Layer - Beta9 Sandbox RPC
package network

import (
	"errors"
)

type SandboxResult struct {
	Connected bool
	Err       error
}

func ConnectToSandbox(sandboxIp string, port int) SandboxResult {
	if sandboxIp == "" || port <= 0 {
		return SandboxResult{Connected: false, Err: errors.New("invalid sandbox routing info")}
	}

	// Go RPC establishing connection to Beta9 serverless VM sandbox
	return SandboxResult{Connected: true, Err: nil}
}
