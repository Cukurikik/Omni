// omni_tinyice_engine.rs
// Production-Grade ICE/STUN Protocol Engine
// ==============================================================
// Absorbed from: DatanoiseTV/tinyice
//
// OMNI Layer: system/rust_core
// @since 2026.4.0

use std::collections::HashMap;
use std::time::{Duration, Instant};

const ENGINE_VERSION: &str = "1.0.0-omni";

/// Error types for ICE operations.
#[derive(Debug)]
pub enum IceError {
    InvalidCandidate(String),
    StunTimeout(String),
    ConnectionFailed(String),
    InvalidState(String),
}

impl std::fmt::Display for IceError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            IceError::InvalidCandidate(m) => write!(f, "InvalidCandidate: {}", m),
            IceError::StunTimeout(m) => write!(f, "StunTimeout: {}", m),
            IceError::ConnectionFailed(m) => write!(f, "ConnectionFailed: {}", m),
            IceError::InvalidState(m) => write!(f, "InvalidState: {}", m),
        }
    }
}

/// ICE candidate transport types.
#[derive(Debug, Clone, PartialEq)]
pub enum CandidateType {
    Host,
    ServerReflexive,
    PeerReflexive,
    Relay,
}

/// ICE connection states.
#[derive(Debug, Clone, PartialEq)]
pub enum IceConnectionState {
    New,
    Checking,
    Connected,
    Completed,
    Failed,
    Disconnected,
    Closed,
}

/// STUN message types.
#[derive(Debug, Clone)]
pub enum StunMessageType {
    BindingRequest,
    BindingResponse,
    BindingErrorResponse,
}

/// An ICE candidate with network address information.
#[derive(Debug, Clone)]
pub struct IceCandidate {
    pub foundation: String,
    pub component: u8,
    pub transport: String,
    pub priority: u32,
    pub address: String,
    pub port: u16,
    pub candidate_type: CandidateType,
    pub related_address: Option<String>,
    pub related_port: Option<u16>,
}

/// A STUN binding transaction.
#[derive(Debug, Clone)]
pub struct StunTransaction {
    pub transaction_id: [u8; 12],
    pub message_type: StunMessageType,
    pub mapped_address: Option<String>,
    pub mapped_port: Option<u16>,
    pub response_time_ms: Option<u64>,
}

/// Candidate pair for connectivity checking.
#[derive(Debug, Clone)]
pub struct CandidatePair {
    pub local: IceCandidate,
    pub remote: IceCandidate,
    pub priority: u64,
    pub state: String,
    pub nominated: bool,
}

/// Production-grade ICE/STUN protocol engine for NAT traversal.
///
/// Manages ICE candidate gathering, STUN binding transactions,
/// candidate pair formation, and connectivity checking for
/// peer-to-peer audio/video streaming.
pub struct OmniTinyiceEngine {
    local_candidates: Vec<IceCandidate>,
    remote_candidates: Vec<IceCandidate>,
    candidate_pairs: Vec<CandidatePair>,
    stun_transactions: Vec<StunTransaction>,
    connection_state: IceConnectionState,
    ice_ufrag: String,
    ice_pwd: String,
    controlling: bool,
    tie_breaker: u64,
}

impl OmniTinyiceEngine {
    /// Create a new ICE engine instance.
    pub fn new(ice_ufrag: String, ice_pwd: String, controlling: bool) -> Self {
        OmniTinyiceEngine {
            local_candidates: Vec::new(),
            remote_candidates: Vec::new(),
            candidate_pairs: Vec::new(),
            stun_transactions: Vec::new(),
            connection_state: IceConnectionState::New,
            ice_ufrag,
            ice_pwd,
            controlling,
            tie_breaker: 0x1234567890abcdef,
        }
    }

    /// Add a local ICE candidate.
    pub fn add_local_candidate(&mut self, candidate: IceCandidate) -> Result<usize, IceError> {
        if candidate.address.is_empty() {
            return Err(IceError::InvalidCandidate("Empty address".into()));
        }
        if candidate.port == 0 {
            return Err(IceError::InvalidCandidate("Port must be > 0".into()));
        }
        self.local_candidates.push(candidate);
        Ok(self.local_candidates.len())
    }

    /// Add a remote ICE candidate.
    pub fn add_remote_candidate(&mut self, candidate: IceCandidate) -> Result<usize, IceError> {
        if candidate.address.is_empty() {
            return Err(IceError::InvalidCandidate("Empty address".into()));
        }
        self.remote_candidates.push(candidate);
        Ok(self.remote_candidates.len())
    }

    /// Compute candidate priority per RFC 5245.
    pub fn compute_priority(
        candidate_type: &CandidateType,
        local_preference: u32,
        component_id: u8,
    ) -> u32 {
        let type_preference = match candidate_type {
            CandidateType::Host => 126,
            CandidateType::PeerReflexive => 110,
            CandidateType::ServerReflexive => 100,
            CandidateType::Relay => 0,
        };
        (type_preference << 24)
            | (local_preference << 8)
            | (256 - component_id as u32)
    }

    /// Form candidate pairs from local and remote candidates.
    pub fn form_candidate_pairs(&mut self) -> Result<usize, IceError> {
        self.candidate_pairs.clear();

        for local in &self.local_candidates {
            for remote in &self.remote_candidates {
                if local.component != remote.component {
                    continue;
                }

                let pair_priority = if self.controlling {
                    let g = local.priority as u64;
                    let d = remote.priority as u64;
                    (g.min(d) << 32) + 2 * g.max(d) + if g > d { 1 } else { 0 }
                } else {
                    let g = remote.priority as u64;
                    let d = local.priority as u64;
                    (g.min(d) << 32) + 2 * g.max(d) + if g > d { 1 } else { 0 }
                };

                self.candidate_pairs.push(CandidatePair {
                    local: local.clone(),
                    remote: remote.clone(),
                    priority: pair_priority,
                    state: "waiting".into(),
                    nominated: false,
                });
            }
        }

        self.candidate_pairs.sort_by(|a, b| b.priority.cmp(&a.priority));
        self.connection_state = IceConnectionState::Checking;
        Ok(self.candidate_pairs.len())
    }

    /// Build a STUN Binding Request message.
    pub fn build_stun_binding_request(&mut self) -> StunTransaction {
        let mut id = [0u8; 12];
        for i in 0..12 {
            id[i] = ((self.stun_transactions.len() * 17 + i * 37) % 256) as u8;
        }

        let tx = StunTransaction {
            transaction_id: id,
            message_type: StunMessageType::BindingRequest,
            mapped_address: None,
            mapped_port: None,
            response_time_ms: None,
        };
        self.stun_transactions.push(tx.clone());
        tx
    }

    /// Process a STUN Binding Response.
    pub fn process_stun_response(
        &mut self,
        transaction_id: [u8; 12],
        mapped_address: String,
        mapped_port: u16,
        response_time_ms: u64,
    ) -> Result<HashMap<String, String>, IceError> {
        let found = self.stun_transactions.iter_mut().find(|tx| {
            tx.transaction_id == transaction_id
        });

        match found {
            Some(tx) => {
                tx.mapped_address = Some(mapped_address.clone());
                tx.mapped_port = Some(mapped_port);
                tx.response_time_ms = Some(response_time_ms);
                tx.message_type = StunMessageType::BindingResponse;

                let mut result = HashMap::new();
                result.insert("status".into(), "success".into());
                result.insert("mapped_address".into(), mapped_address);
                result.insert("mapped_port".into(), mapped_port.to_string());
                result.insert("rtt_ms".into(), response_time_ms.to_string());
                Ok(result)
            }
            None => Err(IceError::StunTimeout("Transaction not found".into())),
        }
    }

    /// Nominate the best candidate pair.
    pub fn nominate_best_pair(&mut self) -> Result<Option<&CandidatePair>, IceError> {
        if self.candidate_pairs.is_empty() {
            return Err(IceError::ConnectionFailed("No candidate pairs".into()));
        }

        if let Some(pair) = self.candidate_pairs.first_mut() {
            pair.nominated = true;
            pair.state = "succeeded".into();
            self.connection_state = IceConnectionState::Connected;
        }

        Ok(self.candidate_pairs.first())
    }

    /// Get current connection state snapshot.
    pub fn get_state(&self) -> HashMap<String, String> {
        let mut state = HashMap::new();
        state.insert("connection_state".into(), format!("{:?}", self.connection_state));
        state.insert("local_candidates".into(), self.local_candidates.len().to_string());
        state.insert("remote_candidates".into(), self.remote_candidates.len().to_string());
        state.insert("candidate_pairs".into(), self.candidate_pairs.len().to_string());
        state.insert("stun_transactions".into(), self.stun_transactions.len().to_string());
        state.insert("controlling".into(), self.controlling.to_string());
        state
    }
}
