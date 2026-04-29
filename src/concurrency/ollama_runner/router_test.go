package ollamarunner

import "testing"

func TestSetupRouter(t *testing.T) {
	server := NewModelServer().Unwrap()
	router := SetupRouter(server)
	if router.IsErr() {
		t.Fatalf("Failed to setup router")
	}
}
