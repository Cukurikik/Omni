package ollama

import (
	"github.com/omni-framework/omni-go/core/result"
	"github.com/omni-framework/omni-go/network/evloop"
)

// StartOllamaServer runs the LLM server on the OMNI event loop
func StartOllamaServer(port int) result.Result[string, error] {
	evloop.Spawn(func() {
		// Serve models
	})
	return result.Ok("Server started")
}
