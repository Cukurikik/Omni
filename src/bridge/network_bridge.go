// ===========================================================================
// OMNI BRIDGE — NETWORK ↔ ALL LAYERS INTERFACE
// ===========================================================================
// Go interface contracts for Network-layer engines. Any network engine
// (Go, JS, Elixir) must satisfy these interfaces to be invocable from
// Domain/Compute/UI layers via the OMNI bridge.
// ===========================================================================

package bridge

import "context"

// NetworkRequest is the canonical payload sent to any network engine.
type NetworkRequest struct {
	Method  string            // "GET", "POST", "MCP_STDIO", "WEBSOCKET"
	URL     string            // Target endpoint
	Headers map[string]string // HTTP headers or MCP metadata
	Body    []byte            // Request body (JSON, binary, etc.)
	Timeout int               // Milliseconds
}

// NetworkResponse is the canonical response from any network engine.
type NetworkResponse struct {
	StatusCode int
	Headers    map[string]string
	Body       []byte
	Error      string // Empty if success
}

// NetworkBridge is the interface all network engines must implement.
type NetworkBridge interface {
	// Send dispatches a request through the network engine.
	Send(ctx context.Context, req NetworkRequest) (*NetworkResponse, error)

	// Healthcheck returns true if the engine is operational.
	Healthcheck() bool

	// Name returns the human-readable engine name.
	Name() string
}

// BroadcastResult holds the outcome of a fan-out to multiple engines.
type BroadcastResult struct {
	EngineName string
	Response   *NetworkResponse
	Err        error
}

// Broadcaster fans out a request to multiple NetworkBridge instances.
func Broadcast(ctx context.Context, bridges []NetworkBridge, req NetworkRequest) []BroadcastResult {
	results := make([]BroadcastResult, len(bridges))
	ch := make(chan BroadcastResult, len(bridges))

	for _, b := range bridges {
		go func(bridge NetworkBridge) {
			resp, err := bridge.Send(ctx, req)
			ch <- BroadcastResult{EngineName: bridge.Name(), Response: resp, Err: err}
		}(b)
	}

	for i := range bridges {
		results[i] = <-ch
	}
	return results
}
