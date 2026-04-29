// OMNI Consul Raft Consensus Engine — System Layer (Rust)
// Absorbing hashicorp/consul discovery leadership
// Deterministic Raft algorithm term election constraints

use std::collections::HashMap;

#[derive(Debug)]
pub enum RaftError {
    NetworkPartition,
}

type Result<T> = std::result::Result<T, RaftError>;

#[derive(Clone, PartialEq, Debug)]
pub enum RaftState {
    Follower,
    Candidate,
    Leader,
}

pub struct NodeStatus {
    pub term: u64,
    pub state: RaftState,
    pub votes_received: u32,
}

pub struct OmniConsulRaftConsensus {
    quorum_size: u32,
    elections_held: u64,
}

impl OmniConsulRaftConsensus {
    pub fn new(total_nodes: u32) -> Self {
        Self { 
            quorum_size: (total_nodes / 2) + 1,
            elections_held: 0
        }
    }

    /// Exact bounds execution representing a Raft voting RPC phase
    pub fn evaluate_election_request(
        &mut self,
        mut current_node: NodeStatus,
        peer_votes_granted: u32
    ) -> Result<NodeStatus> {
        self.elections_held += 1;

        // Follower timeout transition geometry
        if current_node.state == RaftState::Follower {
            current_node.state = RaftState::Candidate;
            current_node.term += 1;
            current_node.votes_received = 1; // votes for self
        }

        if current_node.state == RaftState::Candidate {
            current_node.votes_received += peer_votes_granted;

            if current_node.votes_received >= self.quorum_size {
                current_node.state = RaftState::Leader;
            }
        }

        Ok(current_node)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniConsulRaftConsensus".to_string());
        map.insert("quorum".to_string(), self.quorum_size.to_string());
        map.insert("elections".to_string(), self.elections_held.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
