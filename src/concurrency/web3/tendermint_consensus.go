package web3

import (
	"errors"
	"sync"
)

type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](v T) Result[T]      { return Result[T]{Value: v, Err: nil} }
func Err[T any](e error) Result[T] { return Result[T]{Value: *new(T), Err: e} }

type State string

const (
	Propose   State = "PROPOSE"
	PreVote   State = "PREVOTE"
	PreCommit State = "PRECOMMIT"
	Commit    State = "COMMIT"
)

type ConsensusEngine struct {
	mu           sync.Mutex
	currentState State
	currentRound int
	votes        map[string]int
	totalNodes   int
}

func NewConsensusEngine(totalNodes int) *ConsensusEngine {
	return &ConsensusEngine{
		currentState: Propose,
		currentRound: 0,
		votes:        make(map[string]int),
		totalNodes:   totalNodes,
	}
}

// BFT (Byzantine Fault Tolerant) requires > 2/3 majority
func (c *ConsensusEngine) hasMajority() bool {
	return c.votes["YES"] > (c.totalNodes * 2 / 3)
}

func (c *ConsensusEngine) ProcessVote(nodeID string, vote string) Result[State] {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.currentState == Commit {
		return Err[State](errors.New("block already committed"))
	}

	c.votes[vote]++

	if c.hasMajority() {
		// Transition state machine
		switch c.currentState {
		case Propose:
			c.currentState = PreVote
			c.resetVotes()
		case PreVote:
			c.currentState = PreCommit
			c.resetVotes()
		case PreCommit:
			c.currentState = Commit
		}
	}

	return Ok(c.currentState)
}

func (c *ConsensusEngine) resetVotes() {
	c.votes = make(map[string]int)
}
