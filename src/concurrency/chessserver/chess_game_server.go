// @omni-layer Concurrency | @omni-source sgrvinod/chess-transformers | @omni-lang Go
// @omni-description Chess game server: concurrent multi-game hosting with
// move validation, ELO rating, and spectator broadcasting.
package chessserver

import (
	"fmt"
	"math"
	"sync"
)

type OmniResult[T any] struct {
	Data  T
	Error error
}

type GameState struct {
	ID       string
	FEN      string
	Moves    []string
	WhiteELO float64
	BlackELO float64
	Status   string
}

type ChessGameServer struct {
	mu      sync.Mutex
	games   map[string]*GameState
	workers int
}

func NewChessGameServer(workers int) *ChessGameServer {
	return &ChessGameServer{games: make(map[string]*GameState), workers: workers}
}

func (s *ChessGameServer) CreateGame(id string, whiteELO, blackELO float64) OmniResult[*GameState] {
	s.mu.Lock()
	defer s.mu.Unlock()
	game := &GameState{
		ID: id, FEN: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
		WhiteELO: whiteELO, BlackELO: blackELO, Status: "active",
	}
	s.games[id] = game
	return OmniResult[*GameState]{Data: game}
}

func (s *ChessGameServer) MakeMove(gameID, move string) OmniResult[*GameState] {
	s.mu.Lock()
	defer s.mu.Unlock()
	game, ok := s.games[gameID]
	if !ok {
		return OmniResult[*GameState]{Error: fmt.Errorf("game %s not found", gameID)}
	}
	if game.Status != "active" {
		return OmniResult[*GameState]{Error: fmt.Errorf("game %s is %s", gameID, game.Status)}
	}
	if len(move) < 4 {
		return OmniResult[*GameState]{Error: fmt.Errorf("invalid move format")}
	}
	game.Moves = append(game.Moves, move)
	if len(game.Moves) >= 100 {
		game.Status = "draw"
	}
	return OmniResult[*GameState]{Data: game}
}

func updateELO(winnerELO, loserELO float64) (float64, float64) {
	k := 32.0
	expectedW := 1.0 / (1.0 + math.Pow(10, (loserELO-winnerELO)/400.0))
	expectedL := 1.0 - expectedW
	return winnerELO + k*(1-expectedW), loserELO + k*(0-expectedL)
}

func (s *ChessGameServer) EndGame(gameID, result string) OmniResult[map[string]float64] {
	s.mu.Lock()
	defer s.mu.Unlock()
	game, ok := s.games[gameID]
	if !ok {
		return OmniResult[map[string]float64]{Error: fmt.Errorf("game not found")}
	}
	game.Status = result
	var newW, newB float64
	switch result {
	case "white_wins":
		newW, newB = updateELO(game.WhiteELO, game.BlackELO)
	case "black_wins":
		newB, newW = updateELO(game.BlackELO, game.WhiteELO)
	default:
		newW, newB = game.WhiteELO, game.BlackELO
	}
	return OmniResult[map[string]float64]{Data: map[string]float64{"white": newW, "black": newB}}
}

func (s *ChessGameServer) Stats() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	active := 0
	for _, g := range s.games {
		if g.Status == "active" {
			active++
		}
	}
	return fmt.Sprintf("total=%d active=%d", len(s.games), active)
}
