// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Raft Consensus (OMNI Zero-Mock Implementation)
// Implements deterministic majority voting and leader election math.

pub struct ResultT<T> {
    pub value: Option<T>,
    pub is_ok: bool,
    pub error: String,
}

pub struct VoteRequest {
    pub candidate_id: usize,
    pub candidate_term: u64,
    pub last_log_index: u64,
}

pub struct PeerState {
    pub current_term: u64,
    pub voted_for: Option<usize>,
    pub last_log_index: u64,
}

pub struct ElectionEngine;

impl ElectionEngine {
    // Evaluates a vote request based on Raft safety rules
    pub fn evaluate_vote(peer: &mut PeerState, req: &VoteRequest) -> ResultT<bool> {
        // Rule 1: Reply false if term < currentTerm
        if req.candidate_term < peer.current_term {
            return ResultT { value: Some(false), is_ok: true, error: "".to_string() };
        }
        
        // Update term if candidate term is larger
        if req.candidate_term > peer.current_term {
            peer.current_term = req.candidate_term;
            peer.voted_for = None; // Reset vote for new term
        }
        
        // Rule 2: If votedFor is null or candidateId, and candidate's log is at
        // least as up-to-date as receiver's log, grant vote.
        let log_is_up_to_date = req.last_log_index >= peer.last_log_index;
        
        let can_vote = match peer.voted_for {
            None => true,
            Some(id) if id == req.candidate_id => true,
            _ => false,
        };
        
        if can_vote && log_is_up_to_date {
            peer.voted_for = Some(req.candidate_id);
            return ResultT { value: Some(true), is_ok: true, error: "".to_string() };
        }
        
        ResultT { value: Some(false), is_ok: true, error: "".to_string() }
    }
}
