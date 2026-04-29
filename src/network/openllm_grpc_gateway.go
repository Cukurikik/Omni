// OMNI Network Layer - OpenLLM gRPC Gateway
package network

import (
	"errors"
)

type GatewayResult struct {
	Port int
	Err  error
}

func ServeOpenAIEndpoint(port int) GatewayResult {
	if port < 8000 {
		return GatewayResult{Port: 0, Err: errors.New("invalid port for OpenLLM gateway")}
	}

	// Serves gRPC/REST gateway compatible with OpenAI standard
	return GatewayResult{Port: port, Err: nil}
}
