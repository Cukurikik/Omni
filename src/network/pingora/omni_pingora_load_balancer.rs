// OMNI Pingora Load Balancer Engine — Network Layer (Rust)
// Absorbing cloudflare/pingora memory safe EWMA load balancing
// Exponentially Weighted Moving Average selection math

use std::collections::HashMap;

#[derive(Debug)]
pub enum PingoraError {
    EmptyUpstream,
}

type Result<T> = std::result::Result<T, PingoraError>;

pub struct EwmaUpstream {
    pub id: String,
    pub current_connections: u32,
    pub latency_ewma: f64,
}

pub struct OmniPingoraLoadBalancer {
    balances_executed: u64,
    decay_factor: f64, // alpha
}

impl OmniPingoraLoadBalancer {
    pub fn new(decay: f64) -> Self {
        Self { 
            balances_executed: 0,
            decay_factor: decay,
        }
    }

    /// Evaluates Peak EWMA math representation to select the least loaded upstream bound
    pub fn execute_ewma_selection(
        &mut self,
        upstreams: &mut [EwmaUpstream]
    ) -> Result<String> {
        if upstreams.is_empty() {
            return Err(PingoraError::EmptyUpstream);
        }

        self.balances_executed += 1;

        let mut best_id = String::new();
        let mut min_score = f64::MAX;

        for up in upstreams.iter() {
            // Peak EWMA logic: Score = Connections * EwmaLatency
            // Prevents thundering herd on fast but saturated nodes
            let score = (up.current_connections as f64 + 1.0) * up.latency_ewma;
            
            if score < min_score {
                min_score = score;
                best_id = up.id.clone();
            }
        }

        Ok(best_id)
    }

    /// Exact recursive EWMA math update formula
    pub fn record_latency_sample(
        &mut self,
        upstream: &mut EwmaUpstream,
        observed_latency_ms: f64
    ) {
        // EWMA_t = (alpha * observed) + ((1 - alpha) * EWMA_{t-1})
        upstream.latency_ewma = (self.decay_factor * observed_latency_ms) 
                              + ((1.0 - self.decay_factor) * upstream.latency_ewma);
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniPingoraLoadBalancer".to_string());
        map.insert("selections".to_string(), self.balances_executed.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
