package ollama_runner

import "testing"

func TestSetupRouter(t *testing.T) {
	server := NewModelServer().Unwrap()
	router := SetupRouter(server)
	if router.IsErr() {
		t.Fatalf("Failed to setup router")
	}
}

