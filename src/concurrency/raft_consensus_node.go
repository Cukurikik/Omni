package concurrency

// NodeState represents the state of a Raft consensus node
type NodeState int

const (
	StateFollower NodeState = iota
	StateCandidate
	S
)
