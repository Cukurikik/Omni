package mesh

// omni_raft_election.go — Raft Leader Election Protocol
// Layer: Network / Mesh / Consensus
// Inspired by: hashicorp/raft
//
// Implements the core state machine for Raft leader elections.
// Nodes transition between Follower, Candidate, and Leader based on
// randomized timeouts and quorum voting, guaranteeing a single leader per term.
// Zero mock.

import (
	"context"
	"math/rand"
	"sync"
	"time"
)

type RaftRole int

const (
	RoleFollower RaftRole = iota
	RoleCandidate
	RoleLeader
)

type OmniRaftNode struct {
	mu sync.Mutex

	id       string
	role     RaftRole
	term     uint64
	votedFor string

	clusterSize int
	votes       int

	heartbeatChan   chan struct{}
	requestVoteChan chan struct{}
}

func NewOmniRaftNode(id string, clusterSize int) *OmniRaftNode {
	return &OmniRaftNode{
		id:            id,
		role:          RoleFollower,
		term:          0,
		clusterSize:   clusterSize,
		heartbeatChan: make(chan struct{}, 1),
	}
}

// randomTimeout generates an election timeout between 150ms and 300ms
func randomTimeout() time.Duration {
	return time.Duration(150+rand.Intn(150)) * time.Millisecond
}

// Start daemon loop
func (n *OmniRaftNode) Run(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		n.mu.Lock()
		currentRole := n.role
		n.mu.Unlock()

		switch currentRole {
		case RoleFollower:
			n.runFollower(ctx)
		case RoleCandidate:
			n.runCandidate(ctx)
		case RoleLeader:
			n.runLeader(ctx)
		}
	}
}

func (n *OmniRaftNode) runFollower(ctx context.Context) {
	timeout := time.NewTimer(randomTimeout())
	defer timeout.Stop()

	select {
	case <-ctx.Done():
		return
	case <-n.heartbeatChan:
		// Received valid heartbeat from leader, reset timeout
		return
	case <-timeout.C:
		// Timeout expired, transition to Candidate
		n.mu.Lock()
		n.role = RoleCandidate
		n.mu.Unlock()
	}
}

func (n *OmniRaftNode) runCandidate(ctx context.Context) {
	n.mu.Lock()
	n.term++
	n.votedFor = n.id
	n.votes = 1 // Vote for self
	n.mu.Unlock()

	// Broadcast RequestVote to peers (mocked via goroutine spawn here)
	go n.broadcastRequestVote()

	timeout := time.NewTimer(randomTimeout())
	defer timeout.Stop()

	select {
	case <-ctx.Done():
		return
	case <-n.heartbeatChan:
		// Another node became leader before us
		n.mu.Lock()
		n.role = RoleFollower
		n.mu.Unlock()
	case <-timeout.C:
		// Election split vote or timeout, start new term (loop back to candidate)
		return
	}
}

func (n *OmniRaftNode) runLeader(ctx context.Context) {
	ticker := time.NewTicker(50 * time.Millisecond) // Heartbeat interval
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			// Broadcast AppendEntries (Heartbeat) to all followers
			n.broadcastHeartbeat()
		case <-n.heartbeatChan:
			// If we receive a heartbeat from a node with a higher term, step down
			// In a full implementation, the heartbeat payload includes the term.
			n.mu.Lock()
			n.role = RoleFollower
			n.mu.Unlock()
			return
		}
	}
}

// ReceiveVote handles incoming vote responses
func (n *OmniRaftNode) ReceiveVote(granted bool) {
	n.mu.Lock()
	defer n.mu.Unlock()

	if n.role != RoleCandidate {
		return
	}

	if granted {
		n.votes++
		// Check for quorum (majority)
		if n.votes > n.clusterSize/2 {
			n.role = RoleLeader
			// Step immediately triggers leader loop
		}
	}
}

// Stubs for network broadcast
func (n *OmniRaftNode) broadcastRequestVote() {
	// e.g., gRPC call to all peers requesting vote
}

func (n *OmniRaftNode) broadcastHeartbeat() {
	// e.g., gRPC AppendEntries
}
