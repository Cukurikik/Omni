// OMNI Concurrency Layer: elia_socket_server.go
// Local UNIX socket server bridging Python TUI and OMNI Core.
// Bound: Max 10 simultaneous local clients.

package network

import (
	"sync"
)

const MAX_LOCAL_CLIENTS = 10

type OmniSocketError struct {
	Code    int
	Message string
}

type OmniSocketResult struct {
	Data  interface{}
	Error *OmniSocketError
}

type EliaSocketServer struct {
	activeClients int
	mu            sync.Mutex
}

func NewEliaSocketServer() *EliaSocketServer {
	return &EliaSocketServer{
		activeClients: 0,
	}
}

func (s *EliaSocketServer) AcceptConnection() OmniSocketResult {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.activeClients >= MAX_LOCAL_CLIENTS {
		return OmniSocketResult{
			Data: nil,
			Error: &OmniSocketError{
				Code:    1,
				Message: "Local socket limit exceeded",
			},
		}
	}

	s.activeClients++
	return OmniSocketResult{
		Data:  "connection_accepted",
		Error: nil,
	}
}

func (s *EliaSocketServer) CloseConnection() {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.activeClients > 0 {
		s.activeClients--
	}
}
